# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from power_grid_model_io.obj.array import BatchArray


class UpdateArray(BatchArray):
    data_type = "update"

    id: np.ndarray  # ID of a component, the id should be unique along all components
