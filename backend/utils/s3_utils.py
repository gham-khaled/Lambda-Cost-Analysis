"""S3 utility functions for file operations."""

import boto3
import botocore

client = boto3.client("s3", config=botocore.client.Config(max_pool_connections=50))


def upload_file_to_s3(
    body: str, file_name: str, bucket_name: str, directory: str | None = None
) -> None:
    """
    Upload file content to S3.

    Parameters
    ----------
    body : str
        File content to upload
    file_name : str
        Name of the file
    bucket_name : str
        S3 bucket name
    directory : str, optional
        Directory path within bucket
    """
    filename_s3 = f"{directory}/{file_name}" if directory else file_name
    client.put_object(Body=body, Bucket=bucket_name, Key=filename_s3)


def download_from_s3(
    file_name: str, bucket_name: str, directory: str | None = None
) -> str:
    """
    Download file content from S3.

    Parameters
    ----------
    file_name : str
        Name of the file
    bucket_name : str
        S3 bucket name
    directory : str, optional
        Directory path within bucket

    Returns
    -------
    str
        File content as string
    """
    filename_s3 = f"{directory}/{file_name}" if directory else file_name
    obj = client.get_object(Bucket=bucket_name, Key=filename_s3)
    return obj["Body"].read().decode("utf-8")  # type: ignore[no-any-return]
