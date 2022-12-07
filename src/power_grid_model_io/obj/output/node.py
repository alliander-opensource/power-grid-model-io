# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from power_grid_model_io.obj.output.array import OutputArray


class OutputNodeArray(OutputArray):
    component_type = "node"

    u_pu: np.ndarray  # per-unit voltage magnitude
    u_angle: np.ndarray  # voltage angle
    u: np.ndarray  # voltage magnitude, line-line for symmetric calculation, line-neutral for asymmetric calculation
