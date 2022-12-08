# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Mapping
from typing import Generic, Iterator, Optional, TypeVar

import numpy as np
from power_grid_model.data_types import BatchArray as PgmBatchArray
from power_grid_model.data_types import BatchDataset, SingleDataset

from power_grid_model_io.obj.array import Array, BatchArray, SingleArray

T = TypeVar("T")


class Grid(Mapping[str, Generic[T]]):
    def __iter__(self) -> Iterator[str]:
        for attr in self.__dict__:
            if isinstance(getattr(self, attr), Array):
                yield attr[:-1]

    def __len__(self) -> int:
        return sum(isinstance(getattr(self, attr), Array) for attr in self.__dict__)

    def __getitem__(self, item: str):
        raise KeyError(item)


class SingleGrid(Grid[np.ndarray]):
    def __init__(self, data: Optional[SingleDataset]):
        if data is None:
            return
        for component_name, component_data in data.items():
            component_array = getattr(self, component_name)
            component_array.data = component_data
            component_array.indptr = None

    def __getitem__(self, item: str):
        if item not in self.__dict__ and item + "s" in self.__dict__:
            item += "s"
        if item in self.__dict__:
            attr = self.__dict__[item]
            if isinstance(attr, SingleArray):
                return attr.data
        raise KeyError(item)


class BatchGrid(Grid[PgmBatchArray]):
    def __init__(self, data: Optional[BatchDataset]):
        if data is None:
            return
        for component_name, component_data in data.items():
            component_array = getattr(self, component_name + "s")
            if isinstance(component_data, np.ndarray):
                component_array.data = component_data
                component_array.indptr = None
            else:
                component_array.data = component_data["data"]
                component_array.indptr = component_data["indptr"]

    def __getitem__(self, item: str):
        if item not in self.__dict__ and item + "s" in self.__dict__:
            item += "s"
        if item in self.__dict__:
            attr = self.__dict__[item]
            if isinstance(attr, BatchArray):
                if attr.is_sparse():
                    return {"data": attr.data, "indptr": attr.indptr}
                else:
                    return attr.data
        raise KeyError(item)
