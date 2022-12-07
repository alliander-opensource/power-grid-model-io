# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from power_grid_model_io.obj.input.branch import InputBranchArray


class InputLineArray(InputBranchArray):
    component_type = "line"

    r1: np.ndarray  # positive-sequence serial resistance
    x1: np.ndarray  # positive-sequence serial reactance
    c1: np.ndarray  # positive-sequence shunt capacitance
