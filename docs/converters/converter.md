<!--
SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model project <dynamic.grid.calculation@alliander.com>

SPDX-License-Identifier: MPL-2.0
-->

# Converters

There are 4 types of converters present as of now. 
Here, we shall discuss their basic structure and guidelines for building a custom converter.

Use the examples notebooks to understand how to convert data from the respective formats. 

- **PGM JSON Converter:** Refer to the [PGM JSON Example](../examples/pgm_json_example.ipynb)
- **VisonExcelConverter** Refer to the [Vision Example](../examples/vision_example.ipynb)
- **Pandapower Converter:** Converts [pandapower network](https://pandapower.readthedocs.io/en/stable/elements.html), which is a dictionary of dataframes, to power-grid-model data.

Refer to [converters](../power_grid_model_io.md#converters) in API documentation for more details

## Structure

The `VisonExcelConverter` extends the [tabular converters](tabular_converter.md) for Excel exports of Vision.
All converters are derived from the base {py:class}`power_grid_model_io.converters.base_converter`. 
The usable functions for loading, saving and converting the data are located in the base class. 
The private functions (`_load_data`, `_parse_data` and `_serialize_data`) are overloaded based on the specific type of converter (ie. excel, json or pandapower). 
It is recommended to create any custom converter in a similar way.

## Instantiation

A converter object can be instantiated in the following way. For eg, for a `PgmJsonConverter`,

```python
from power_grid_model_io.converters.pgm_json_converter import PgmJsonConverter

converter = PgmJsonConverter(source_file=source, destination_file=destination)
```

The usable methods of converters for loading and saving the data are described below.

## Loading data

Use the methods load_input_data(), load_update_data(), load_sym_output_data() or load_asym_output_data() to load the relevant data to the converter.
The Converter can be initialised with `source_file` containing path to source data. Or alternatively, the data can be provided as an argument to the load function.

In addition to the power-grid-model input data, other miscellaneous information in the source file not used in calculations by power-grid-model gets stored under `extra_info`

```python
input_data, extra_info = converter.load_input_data(data=example_data)
```

## Saving Data

It is possible to save the data in the format of the converter.
The Converter can be instantiated with a path given to `destination_file`. 
Alternatively, the destination path can be provided in the save function.
You can also add additional information about each component in the form of `extra_info` generated by [Load data](converter.md#load-data) to be saved along with it.

```python
converter.save(example_data, extra_info=example_extra_info, destination=destination_path)
```
