# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from power_grid_model_io.obj.update.array import UpdateArray


class UpdateBranchArray(UpdateArray):
    from_status: np.ndarray
    to_status: np.ndarray
