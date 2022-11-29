# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import logging
from pathlib import Path
from time import time

import structlog
from power_grid_model import PowerGridModel

from power_grid_model_io.converters.pgm_json_converter import PgmJsonConverter
from power_grid_model_io.converters.sim_bench_converter import SimBenchConverter

# Logging
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG))
log = structlog.get_logger(__name__)

# Load source
simbench_code = "1-complete_data-mixed-all-0-sw"
simbench_converter = SimBenchConverter(simbench_code)

# Convert to PGM
start = time()
input_data, extra_info = simbench_converter.load_input_data()
log.info("Loading and converting input", duration=time() - start)

# Store the source data in JSON format
start = time()
converter = PgmJsonConverter(destination_file=f"data/sim-bench/{simbench_code}_input.json")
converter.save(data=input_data, extra_info=extra_info)
log.info("Saving input data", duration=time() - start)

# Perform power flow calculation
start = time()
grid = PowerGridModel(input_data=input_data)
output_data = grid.calculate_power_flow()
log.info("Calculating powerflow", duration=time() - start)

# Store the result data in JSON format
start = time()
converter = PgmJsonConverter(destination_file=f"data/sim-bench/{simbench_code}_output.json")
converter.save(data=output_data, extra_info=extra_info)
log.info("Saving output data", duration=time() - start)
