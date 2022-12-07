# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from power_grid_model import initialize_array


class Array:
    data_type: str
    component_type: str
    data: Optional[np.ndarray] = None

    def initialize(self, shape):
        self.data = np.empty(shape=shape)

    def __getattr__(self, item):
        if self.data is None:
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{item}'; "
                                 f"no data in {type(self).__name__}.data")
        if item not in self.data.dtype.names:
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{item}'; "
                                 f"choose from: " + ", ".join(self.data.dtype.names))
        return self.data[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        if self.data is None or key not in self.data.dtype.names:
            self.__dict__[key] = value
        else:
            self.data[key] = value

    def __len__(self) -> int:
        if not hasattr(self, "data"):
            return 0
        return self.data.shape[-1]


class SingleArray(Array):
    def __init__(self, n_objects: Optional[int] = None):
        if n_objects is not None:
            self.initialize(n_objects)

    def initialize(self, n_objects: int):
        if not isinstance(n_objects, int):
            raise TypeError()
        self.data = initialize_array(data_type=self.data_type, component_type=self.component_type, shape=n_objects)

    def as_np(self):
        return self.data

    def as_df(self):
        return pd.DataFrame(self.as_np())

    def __getitem__(self, item: Union[int, slice]) -> np.ndarray:
        if self.data is None:
            raise IndexError(f"No data in {type(self).__name__}")
        return self.data[item]


class BatchArray(Array):
    indptr: Optional[np.ndarray] = None

    def __init__(self, n_objects: Optional[Union[int, List[int]]] = None, n_batches: Optional[int] = None):
        if n_objects is not None:
            self.initialize(n_objects=n_objects, n_batches=n_batches)

    def initialize(self, n_objects: Optional[Union[int, List[int]]] = None, n_batches: Optional[int] = None):
        if isinstance(n_objects, int):
            if n_batches is None:
                n_batches = 1
            shape = (n_batches, n_objects)
        elif isinstance(n_objects, list):
            indptr = [0]
            for n in n_objects:
                indptr.append(indptr[-1] + n)
            shape = indptr[-1]
            self.indptr = np.array(indptr)
        else:
            raise TypeError()
        self.data = initialize_array(data_type=self.data_type, component_type=self.component_type, shape=shape)

    def is_batch(self):
        return self.data is not None and (self.data.ndim > 1 or self.is_sparse())

    def is_dense(self):
        return self.indptr is None

    def is_sparse(self):
        return self.indptr is not None

    def as_np(self):
        if self.is_sparse():
            raise TypeError("Can't convert a sparse array to a NumPy array")
        return self.data

    def as_df(self):
        if self.is_batch():
            raise TypeError("Can't convert a batch array to a Pandas DataFrame")
        return pd.DataFrame(self.as_np())

    def batch(self, batch: int) -> np.ndarray:
        if self.data is None:
            raise ValueError(f"No data in {type(self).__name__}")
        if self.data.ndim == 1 and self.indptr is not None:
            return self.data[self.indptr[batch]:self.indptr[batch + 1]]
        return self.data[batch]

    def __getitem__(self, item: Union[int, slice, Tuple[Union[int, slice], Union[int, slice]]]) -> np.ndarray:

        if isinstance(item, tuple):
            batches, items = item
        else:
            batches = item
            items = None

        if isinstance(batches, int):
            data = self.batch(batches)
        elif self.is_sparse():
            raise IndexError("Can't index multiple batches in a sparse array")
        else:
            data = self.data[batches]

        if items is not None:
            data = data[items]

        return data
