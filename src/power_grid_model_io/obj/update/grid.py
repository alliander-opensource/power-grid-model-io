# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Optional

from power_grid_model.data_types import BatchDataset
from power_grid_model_io.obj.grid import BatchGrid
from power_grid_model_io.obj.update.line import UpdateLineArray


class UpdateGrid(BatchGrid):
    line: UpdateLineArray

    def __init__(self, data: Optional[BatchDataset] = None):
        self.line = UpdateLineArray()
        super().__init__(data=data)
