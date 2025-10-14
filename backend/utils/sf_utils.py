"""Step Functions utilities for parameter handling."""

import json
from datetime import datetime
from functools import partial
from typing import Any

from utils.multithread_utils import multi_thread
from utils.s3_utils import download_from_s3, upload_file_to_s3

s3_params_bucket = "step-functions-params"


def upload_params(
    params: list[Any],
    bucket_name: str = "step-functions-params",
    directory_name: str = "",
    directory_prefix: bool = True,
) -> list[dict[str, str]]:
    """
    Upload parameters to S3 for Step Functions processing.

    Parameters
    ----------
    params : list
        Parameters to upload
    bucket_name : str, default="step-functions-params"
        S3 bucket name
    directory_name : str, default=""
        Directory path in bucket
    directory_prefix : bool, default=True
        Whether to add timestamp prefix to directory

    Returns
    -------
    list of dict
        S3 locations of uploaded parameters
    """
    now_date = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    directory_name = directory_name + now_date if directory_prefix else directory_name

    params_filename = [
        (f"params{i}.json", heaters_info) for i, heaters_info in enumerate(params)
    ]
    partial_upload_single_params_file = partial(
        upload_single_params_file, bucket_name=bucket_name, directory=directory_name
    )
    s3_params = multi_thread(partial_upload_single_params_file, params_filename, 20)
    return s3_params  # type: ignore[no-any-return]


def upload_single_params_file(
    params_filename: tuple[str, Any], bucket_name: str, directory: str
) -> dict[str, str]:
    """
    Upload a single parameter file to S3.

    Parameters
    ----------
    params_filename : tuple
        Tuple of (filename, content)
    bucket_name : str
        S3 bucket name
    directory : str
        Directory path in bucket

    Returns
    -------
    dict
        S3 location of uploaded file
    """
    filename, heaters_info = params_filename
    upload_file_to_s3(json.dumps(heaters_info), filename, bucket_name, directory)
    return {"filename": filename, "bucket": bucket_name, "directory": directory}


def upload_divided_params(
    params: list[Any],
    divider: int,
    bucket_name: str = "step-functions-params",
    directory_name: str = "",
) -> list[dict[str, str]]:
    """
    Divide parameters into chunks and upload to S3.

    Parameters
    ----------
    params : list
        Parameters to divide and upload
    divider : int
        Chunk size for division
    bucket_name : str, default="step-functions-params"
        S3 bucket name
    directory_name : str, default=""
        Directory path in bucket

    Returns
    -------
    list of dict
        S3 locations of uploaded chunks
    """
    return upload_params(divide_list(params, divider), bucket_name, directory_name)


def divide_list(list_to_divide: list[Any], divider: int) -> list[list[Any]]:
    """
    Divide list into chunks of specified size.

    Parameters
    ----------
    list_to_divide : list
        List to divide
    divider : int
        Maximum items per chunk

    Returns
    -------
    list of list
        Divided chunks
    """
    return [
        list_to_divide[x : x + divider] for x in range(0, len(list_to_divide), divider)
    ]


def download_parameters_from_s3(file_params: dict[str, str]) -> Any:
    """
    Download and parse parameters from S3.

    Parameters
    ----------
    file_params : dict
        S3 file location with filename, bucket, and directory

    Returns
    -------
    Any
        Parsed JSON parameters
    """
    filename_params = file_params["filename"]
    bucket_params = file_params["bucket"]
    directory_params = file_params.get("directory")
    return json.loads(
        download_from_s3(filename_params, bucket_params, directory_params)
    )
