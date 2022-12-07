# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from power_grid_model_io.obj.input.array import InputArray


class InputNodeArray(InputArray):
    component_type = "node"

    u_rated: np.ndarray  # rated line-line voltage
