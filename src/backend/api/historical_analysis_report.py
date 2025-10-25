"""API endpoint to retrieve historical analysis reports."""

import json
import os
from typing import Any

import boto3
from aws_lambda_powertools import Logger

from backend.api.app import app

logger = Logger()

s3_client = boto3.client("s3")

bucket_name = os.environ["BUCKET_NAME"]

prefix = "summaries/"


@app.get("/reportSummaries")  # type: ignore[misc]
def list_historical_reports() -> dict[str, Any]:
    """Retrieve paginated list of historical analysis reports."""
    query_params = app.current_event.query_string_parameters or {}
    continuation_token = query_params.get("continuationToken")
    max_keys = int(query_params.get("rowsPerPage", 10))

    logger.info(
        "Fetching historical reports",
        extra={"max_keys": max_keys, "has_continuation": bool(continuation_token)},
    )

    list_params: dict[str, Any] = {
        "Bucket": bucket_name,
        "Prefix": prefix,
        "MaxKeys": max_keys,
    }
    if continuation_token:
        list_params["ContinuationToken"] = continuation_token

    # List objects in the specified S3 bucket and prefix
    response = s3_client.list_objects_v2(**list_params)

    # Get continuation token from the event if present
    if "Contents" not in response:
        return {"message": "No files found."}

    # Extract the JSON files
    json_files = [
        content["Key"]
        for content in response["Contents"]
        if content["Key"].endswith(".json")
    ]

    # Fetch the content of each JSON file
    json_contents = []
    # TODO: Add multithreading for faster retrieval
    for file_key in json_files:
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = file_obj["Body"].read().decode("utf-8")
        json_contents.append(json.loads(file_content))

    result: dict[str, Any] = {
        "jsonContents": json_contents,
        "message": "Successfully found analysis summaries",
    }

    # Add the continuation token to the result if more files are available
    if response.get("IsTruncated"):
        result["continuationToken"] = response.get("NextContinuationToken")

    logger.info("Retrieved historical reports", extra={"count": len(json_contents)})
    return result


# Lambda handler is in app.py - this module just registers routes
