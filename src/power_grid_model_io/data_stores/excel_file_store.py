# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
Excel File Store
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

from power_grid_model_io.data_stores.base_data_store import BaseDataStore
from power_grid_model_io.data_types import TabularData


class ExcelFileStore(BaseDataStore[TabularData]):
    """
    Excel File Store

    The first row of each sheet is expected to contain the column names, unless specified differently by an extension
    of this class. Columns with duplicate names (on the same sheet) are either removed (if they contain exactly the
    same values) or renamed.
    """

    __slots__ = ("_file_paths", "_header_rows")

    _unnamed_pattern: re.Pattern = re.compile(r"Unnamed: \d+_level_\d+")

    def __init__(self, file_path: Optional[Path] = None, **extra_paths: Path):
        super().__init__()

        # Create a list of all supplied file paths:
        # [(None, file_path), [extra_name[0], extra_path[0]), [extra_name[1], extra_path[1]), ...]
        self._file_paths: Dict[str, Path] = {}
        if file_path is not None:
            self._file_paths[""] = file_path
        for name, path in extra_paths.items():
            self._file_paths[name] = path

        for name, path in self._file_paths.items():
            if path.suffix.lower() not in {".xls", ".xlsx"}:
                name = name.title() if name else "Excel"
                raise ValueError(f"{name} file should be a .xls or .xlsx file, {path.suffix} provided.")

        self._header_rows: List[int] = [0]

    def files(self) -> Dict[str, Path]:
        """
        Read-only accessor
        """
        return self._file_paths.copy()

    def load(self) -> TabularData:
        """
        Load one or more Excel file as tabular data.
        """
        data: Dict[str, pd.DataFrame] = {}
        for name, path in self._file_paths.items():
            with path.open(mode="rb") as file_pointer:
                spreadsheet = pd.read_excel(io=file_pointer, sheet_name=None, header=self._header_rows)
            for sheet_name, sheet_data in spreadsheet.items():
                sheet_data = self._remove_unnamed_column_placeholders(data=sheet_data, sheet_name=sheet_name)
                sheet_data = self._handle_duplicate_columns(data=sheet_data, sheet_name=sheet_name)
                if name:
                    sheet_name = f"{name}.{sheet_name}"
                if sheet_name in data:
                    raise ValueError(f"Duplicate sheet name '{sheet_name}'")
                data[sheet_name] = sheet_data

        return TabularData(**data)

    def save(self, data: TabularData) -> None:
        """
        Load one or more Excel file as tabular data.
        """

        # First group all sheets per file. Each sheet name that starts with a file name is assigned to that file.
        # Sheets that don't start with a file name are assigned to the first file.
        sheets: Dict[str, Dict[str, pd.DataFrame]] = {file_name: {} for file_name in self._file_paths}
        for sheet_name, sheet_data in data.items():
            if "." in sheet_name:
                file_name, alt_sheet_name = sheet_name.split(".", maxsplit=1)
                if file_name in self._file_paths:
                    sheets[file_name][alt_sheet_name] = sheet_data
                    continue
            sheets[""][sheet_name] = sheet_data

        # Create an Excel file if there is at least one sheet.
        for file_name, file_path in self._file_paths.items():
            if not sheets[file_name]:
                continue
            with file_path.open(mode="wb") as file_pointer:
                for sheet_name, sheet_data in sheets[file_name].items():
                    sheet_data.to_excel(
                        excel_writer=file_pointer,
                        sheet_name=sheet_name,
                    )

    def _remove_unnamed_column_placeholders(self, data: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        if data.empty:
            return data

        def is_unnamed(col_name):
            col_is_unnamed = self._unnamed_pattern.fullmatch(str(col_name))
            self._log.warning("Column is renamed", sheet_name=sheet_name, col_name=col_name, new_name="")
            return col_is_unnamed

        columns = (tuple("" if is_unnamed(idx) else idx for idx in col_idx) for col_idx in data.columns.values)
        return pd.DataFrame(data, columns=pd.MultiIndex.from_tuples(columns))

    def _handle_duplicate_columns(self, data: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        if data.empty:
            return data

        grouped = self._group_columns_by_index(data=data)
        to_remove, to_rename = self._check_duplicate_values(sheet_name=sheet_name, data=data, grouped=grouped)

        columns = data.columns.values
        if to_rename:
            for col_idx, new_name in to_rename.items():
                self._log.warning(
                    "Column is renamed",
                    sheet_name=sheet_name,
                    col_name=columns[col_idx],
                    new_name=new_name,
                    col_idx=col_idx,
                )
                columns[col_idx] = new_name
            data.columns = pd.MultiIndex.from_tuples(columns)

        for col_idx in to_remove:
            self._log.debug("Column is removed", sheet_name=sheet_name, col_name=columns[col_idx], col_idx=col_idx)
        all_columns = set(range(len(data.columns)))
        to_keep = all_columns - to_remove
        return data.iloc[:, sorted(to_keep)]

    def _group_columns_by_index(self, data: pd.DataFrame) -> Dict[Tuple[str, ...], Set[int]]:
        grouped: Dict[Tuple[str, ...], Set[int]] = {}
        columns = data.columns.values
        for col_idx, col_name in enumerate(columns):
            col_name = (col_name,) if not isinstance(col_name, tuple) else col_name
            if col_name not in grouped:
                grouped[col_name] = set()
            grouped[col_name].add(col_idx)
        return grouped

    def _check_duplicate_values(
        self, sheet_name: str, data: pd.DataFrame, grouped: Dict[Tuple[str, ...], Set[int]]
    ) -> Tuple[Set[int], Dict[int, Tuple[str, ...]]]:

        to_remove: Set[int] = set()
        to_rename: Dict[int, Tuple[str, ...]] = {}

        for col_name, col_idxs in grouped.items():

            # No duplicate column names
            if len(col_idxs) == 1:
                continue
            # Select the first column as a reference
            ref_idx = min(col_idxs)

            # Select the rest as duplicates
            dup_idxs = col_idxs - {ref_idx}

            same_values = all(data.iloc[:, dup_idx].equals(data.iloc[:, ref_idx]) for dup_idx in dup_idxs)
            if same_values:
                self._log.warning(
                    "Found duplicate column names, with same data",
                    sheet_name=sheet_name,
                    column=col_name,
                    col_idx=sorted(col_idxs),
                )
                to_remove |= dup_idxs
            else:
                self._log.error(
                    "Found duplicate column names, with different data",
                    sheet_name=sheet_name,
                    column=col_name,
                    col_idx=sorted(col_idxs),
                )
                for counter, dup_idx in enumerate(sorted(dup_idxs), start=2):
                    to_rename[dup_idx] = (f"{col_name[0]}_{counter}",) + col_name[1:]

        return to_remove, to_rename
