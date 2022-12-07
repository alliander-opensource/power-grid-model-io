# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from power_grid_model_io.obj.output.array import OutputArray


class OutputBranchArray(OutputArray):
    p_from: np.ndarray  # active power flowing into the branch at from-side
    q_from: np.ndarray  # reactive power flowing into the branch at from-side
    p_to: np.ndarray  # active power flowing into the branch at to-side
    q_to: np.ndarray  # reactive power flowing into the branch at to-side
