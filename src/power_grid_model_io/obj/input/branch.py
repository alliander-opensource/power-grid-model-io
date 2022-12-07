# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from power_grid_model_io.obj.input.array import InputArray


class InputBranchArray(InputArray):
    from_node: np.ndarray
    to_node: np.ndarray
    from_status: np.ndarray
    to_status: np.ndarray
