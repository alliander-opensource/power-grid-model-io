# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from power_grid_model_io.obj.array import BatchArray


class OutputArray(BatchArray):
    symmetrical: bool = True

    @property
    def data_type(self) -> str:
        return "sym_output" if self.symmetrical else "asym_output"

    id: np.ndarray  # ID of a component, the id should be unique along all components
