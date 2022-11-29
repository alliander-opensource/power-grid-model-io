# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from power_grid_model_io.utils.download import (
    download,
    download_and_extract,
    extract,
    get_download_path,
    get_url_headers,
)


def test_get_download_path():
    assert callable(get_download_path)


def test_get_url_headers():
    assert callable(get_url_headers)


def test_download():
    assert callable(download)


def test_extract():
    assert callable(extract)


def test_download_and_extract():
    assert callable(download_and_extract)
