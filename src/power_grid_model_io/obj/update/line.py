# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from power_grid_model_io.obj.update.branch import UpdateBranchArray


class UpdateLineArray(UpdateBranchArray):
    component_type = "line"
