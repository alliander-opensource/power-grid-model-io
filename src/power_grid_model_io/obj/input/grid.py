# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0
from typing import Optional

from power_grid_model.data_types import SingleDataset
from power_grid_model_io.obj.grid import SingleGrid
from power_grid_model_io.obj.input.line import InputLineArray
from power_grid_model_io.obj.input.node import InputNodeArray


class InputGrid(SingleGrid):
    node: InputNodeArray
    line: InputLineArray

    def __init__(self, data: Optional[SingleDataset] = None):
        self.node = InputNodeArray()
        self.line = InputLineArray()
        super().__init__(data=data)
