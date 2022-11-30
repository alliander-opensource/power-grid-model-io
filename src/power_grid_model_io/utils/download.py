# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model IO project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
Helper functions to download (and store) files from the internet
"""

import hashlib
import re
import shutil
import zipfile
from pathlib import Path
from typing import ByteString, Callable, Optional, Tuple
from urllib import request

import structlog
from tqdm import tqdm


def download_and_extract(
    url: str, dir_path: Optional[Path] = None, file_path: Optional[Path] = None, overwrite: bool = False
) -> Path:
    """
    Download a file from a URL and store it locally, extract the contents and return the path to the contents.

    Args:
        url:       The url to the .zip file
        dir_path:  An optional dir path to store the downloaded file. If no dir_path is given the current working dir
                   will be used.
        file_path: An optional file path (absolute or relative to dir_path). If no file_path is given, a file name is
                   generated based on the url
        overwrite: Should we download the file, even if we have downloaded already (and the file size still matches)?

    Returns:
        The path to the downloaded file
    """
    src_file_path = download(url=url, file_path=file_path, dir_path=dir_path, overwrite=overwrite)
    dst_dir_path = src_file_path.with_suffix("")
    if overwrite and dst_dir_path.is_dir():
        shutil.rmtree(dst_dir_path)
    return extract(src_file_path=src_file_path, dst_dir_path=dst_dir_path, skip_if_exists=not overwrite)


def download(
    url: str, file_path: Optional[Path] = None, dir_path: Optional[Path] = None, overwrite: bool = False
) -> Path:
    """
    Download a file from a URL and store it locally

    Args:
        url:       The url to the file
        file_path: An optional file path (absolute or relative to dir_path). If no file_path is given, a file name is
                   generated based on the url
        dir_path:  An optional dir path to store the downloaded file. If no dir_path is given the current working dir
                   will be used.
        overwrite: Should we download the file, even if we have downloaded already (and the file size still matches)?

    Returns:
        The path to the downloaded file
    """
    status_code, remote_size, remote_file_name = get_url_headers(url=url)
    if status_code != 200:
        raise IOError(f"Could not download from URL, status={status_code}")

    if file_path is None and remote_file_name:
        file_path = Path(remote_file_name)

    file_path = get_download_path(dir_path=dir_path, file_path=file_path, data=url.encode())
    log = structlog.get_logger(__name__).bind(url=url, file_path=file_path)

    if file_path.is_file():
        if overwrite:
            log.debug("Forced re-downloading existing file")
        else:
            local_size = file_path.stat().st_size
            if local_size == remote_size:
                log.debug("Skip downloading existing file")
                return file_path
            log.debug(
                "Re-downloading existing file, because the size has changed",
                local_size=local_size,
                remote_size=remote_size,
            )
    else:
        log.debug("Downloading file")

    def progress_hook(progress_bar: tqdm) -> Callable[[int, int, int], None]:
        last_block = [0]

        def update_progress_bar(block_num: int, block_size: int, file_size: int) -> None:
            if file_size > 0:
                progress_bar.total = file_size
            progress_bar.update((block_num - last_block[0]) * block_size)
            last_block[0] = block_num

        return update_progress_bar

    # Download to a temp file first, so the results are not stored if the transfer fails
    with tqdm(desc="Downloading", unit="B", unit_scale=True, leave=True) as progress_bar:
        temp_file, _headers = request.urlretrieve(url, reporthook=progress_hook(progress_bar))

    # Check if the file contains any content
    temp_path = Path(temp_file)
    if temp_path.stat().st_size == 0:
        log.warning("Downloaded an empty file")

    # Move the file to it's final destination
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.unlink(missing_ok=True)
    temp_path.rename(file_path)
    log.debug("Downloaded file", file_size=file_path.stat().st_size)

    return file_path


def get_url_headers(url: str) -> Tuple[int, int, str]:
    """
    Retrieve the file size of a given URL (based on it's header)

    Args:
        url: The url to the file

    Return:
        The file size in bytes
    """
    with request.urlopen(url) as context:
        status_code = context.status
        headers = context.headers
    file_size = int(headers.get("Content-Length", 0))
    matches = re.findall(r"filename=\"(.+)\"", headers.get("Content-Disposition", ""))
    file_name = matches[0] if matches else None

    return status_code, file_size, file_name


def get_download_path(dir_path: Optional[Path], file_path: Optional[Path], data=Optional[ByteString]) -> Path:
    """
    Determine the file path based on dir_path, file_path and/or data

    Args:
        dir_path:  An optional dir path to store the downloaded file. If no dir_path is given the system's temp dir will
                   be used. Use Path(".") if you intend to use the current working directory.
        file_path: An optional file path (absolute or relative to dir_path). If no file_path is given, a file name is
                   generated based on the url
        data:      A bytestring that can be used to generate a filename.
    """

    # If no file_path is given, generate a file name
    if file_path is None:
        try:
            sha256 = hashlib.sha256()
            sha256.update(data)
            hash_str = sha256.hexdigest()
        except (TypeError, ValueError) as ex:
            raise ValueError(f"Can't auto generate a file name for a {type(data).__name__}.") from ex
        file_path = Path(__name__) / f"{hash_str}.download"

    # If no dir_path is given, use current working dir
    elif dir_path is None:
        dir_path = Path(".")

    # Combine the two paths
    file_path = (dir_path / file_path).resolve() if dir_path else file_path.resolve()

    # If the file_path exists, it should be a file (not a dir)
    if file_path.exists() and not file_path.is_file():
        raise ValueError(f"Invalid file path: {file_path}")

    return file_path


def extract(src_file_path: Path, dst_dir_path: Optional[Path] = None, skip_if_exists=True) -> Path:
    """
    Extract a .zip file and return the destination dir

    Args:
        src_file_path: The .zip file to extract.
        dst_dir_path: An optional destination path. If none is given, the src_file_path without .zip extension is used.
        skip_if_exists: If true, it returns the dir path, otherwise raise an exception.

    Returns: The path where the files are extracted

    """
    if src_file_path.suffix.lower() != ".zip":
        raise ValueError(f"Only files with .zip extension are supported, got {src_file_path}")
    if dst_dir_path is None:
        dst_dir_path = src_file_path.with_suffix("")

    log = structlog.get_logger(__name__).bind(src_file_path=src_file_path, dst_dir_path=dst_dir_path)

    if dst_dir_path.exists():
        if not dst_dir_path.is_dir():
            raise NotADirectoryError(f"Destination dir {dst_dir_path} exists and is not a directory")
        if not skip_if_exists:
            raise FileExistsError(f"Destination dir {dst_dir_path} exists and is not empty")
        log.debug("Skip extraction, destination dir exists")

    else:
        # Create the destination directory
        dst_dir_path.mkdir(parents=True, exist_ok=True)

        # Extract per file, so we can show a progress bar
        with zipfile.ZipFile(src_file_path, "r") as zip_file:
            file_list = zip_file.namelist()
            for file_path in tqdm(desc="Extracting", iterable=file_list, total=len(file_list), unit="file", leave=True):
                zip_file.extract(member=file_path, path=dst_dir_path)

    # If the zip files contains a single directory with the same name as the zip file, return that dir
    contents = list(dst_dir_path.iterdir())
    if len(contents) == 1 and contents[0].is_dir() and contents[0].name == src_file_path.stem:
        dst_dir_path = contents[0]

    return dst_dir_path
