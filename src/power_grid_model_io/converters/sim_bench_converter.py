# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
Sim Bench Converter: Download, extract and convert a sim bench dataset to PGM
"""

import re
from pathlib import Path
from tempfile import gettempdir
from typing import Optional

import pandas as pd

from power_grid_model_io.converters.tabular_converter import TabularConverter
from power_grid_model_io.data_stores.csv_dir_store import CsvDirStore
from power_grid_model_io.data_types import TabularData
from power_grid_model_io.utils.download import download_and_extract

DEFAULT_MAPPING_FILE = Path(__file__).parent.parent / "config" / "csv" / "sim_bench.yaml"
DEFAULT_DOWNLOAD_URL = "http://141.51.193.167/simbench/gui/usecase/download/?simbench_code={simbench_code:s}&format=csv"

NODE_PATTERN = re.compile(r"^node[A-Z]+$")


class SimBenchConverter(TabularConverter):
    """
    Sim Bench Converter: Download, extract and convert a sim bench dataset to PGM
    """

    __slots__ = ("_simbench_code", "_download_url", "_download_dir")

    def __init__(self, simbench_code: Optional[str] = None, download_dir: Optional[Path] = None):
        super().__init__(mapping_file=DEFAULT_MAPPING_FILE)
        self.simbench_code: Optional[str] = simbench_code
        self._download_url: Optional[str] = None
        self._download_dir: Path = download_dir or Path(gettempdir())
        if simbench_code is not None:
            self.set_download_url(DEFAULT_DOWNLOAD_URL.format(simbench_code=simbench_code))

    def set_download_url(self, url: str):
        """
        Use a custom sim bench URL
        """
        self._download_url = url

    def _load_data(self, data: Optional[TabularData]) -> TabularData:
        if data is None and self._source is None and self._download_url is not None:
            try:
                csv_dir = download_and_extract(self._download_url, dir_path=self._download_dir)
            except ValueError as ex:
                if str(ex).endswith(".download"):
                    raise ValueError(f"Invalid SimBench dataset URL: {self._download_url}") from None
                raise ex
            self._source = CsvDirStore(csv_dir, delimiter=";")
        return super()._load_data(data=data)

    def _id_lookup(self, component: str, row: pd.Series) -> int:
        """
        Overwrite the default id_lookup method.
        For SimBench files Node columns can be called nodeA, nodeB, etc. Therefore, the id column of the nodes is
        renamed to node_id and all nodeXX columns are also renamed to node_id.
        """
        data = {NODE_PATTERN.sub(col, "node_id"): val for col, val in row.to_dict().items()}
        if component == "node":
            data = {"node_id" if col == "id" else col: val for col, val in data.items()}
        items = sorted(data.items(), key=lambda x: str(x[0]))
        key = component + ":" + ",".join(f"{k}={v}" for k, v in items)
        return self._lookup(item={"component": component, "row": data}, key=key)
