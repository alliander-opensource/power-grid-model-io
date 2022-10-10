import numpy as np
import pytest
from power_grid_model import initialize_array
from power_grid_model.utils import convert_python_to_numpy

from power_grid_model_io.converters.pgm_converter import PgmConverter


@pytest.fixture
def converter():
    converter = PgmConverter()
    return converter


def test_converter__parse_data(converter: PgmConverter):
    with pytest.raises(TypeError, match="Raw data should be either a list or a dictionary!"):
        converter._parse_data(data="str", data_type="input")  # type: ignore

    input_data = {
        "node": [
            {"id": 1, "u_rated": 400.0},
            {"id": 2, "u_rated": 400.0},
        ]
    }

    # test for input dataset
    pgm_data = converter._parse_data(data=input_data, data_type="input")
    assert len(pgm_data) == 1
    assert len(pgm_data["node"]) == 2
    assert [1, 2] in pgm_data["node"]["id"]
    assert [400.0, 400.0] in pgm_data["node"]["u_rated"]

    batch_data = [
        {"sym_load": [{"id": 3, "p_specified": 1.0}]},
        {"sym_load": [{"id": 3, "p_specified": 2.0}, {"id": 4, "p_specified": 3.0}]},
    ]
    # test for batch dataset
    pgm_batch_data = converter._parse_data(data=batch_data, data_type="update")
    assert len(pgm_batch_data) == 1
    assert (pgm_batch_data["sym_load"]["indptr"] == np.array([0, 1, 3])).all()
    assert (pgm_batch_data["sym_load"]["data"]["id"] == [3, 3, 4]).all()
    assert (pgm_batch_data["sym_load"]["data"]["p_specified"] == [1.0, 2.0, 3.0]).all()
