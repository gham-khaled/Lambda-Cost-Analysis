"""API endpoint to retrieve historical analysis reports."""

import json
import logging
import os
from typing import Any

import boto3
from api.cors_decorator import cors_header

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

bucket_name = os.environ["BUCKET_NAME"]

prefix = "summaries/"


@cors_header  # type: ignore[misc]
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Retrieve paginated list of historical analysis reports.

    Parameters
    ----------
    event : dict
        Lambda event with query parameters (continuationToken, rowsPerPage)
    context : Any
        Lambda context

    Returns
    -------
    dict
        API Gateway response with report summaries
    """
    parameters = event.get("queryStringParameters", {})
    logger.info(f"Parameters: {parameters}")
    continuation_token = parameters.get("continuationToken", None)
    max_keys = int(parameters.get("rowsPerPage", 10))

    list_params = {"Bucket": bucket_name, "Prefix": prefix, "MaxKeys": max_keys}
    if continuation_token:
        list_params["ContinuationToken"] = continuation_token

    try:
        # List objects in the specified S3 bucket and prefix
        response = s3_client.list_objects_v2(**list_params)

        # Get continuation token from the event if present
        if "Contents" not in response:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No files found."}),
            }

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
        result = {
            "jsonContents": json_contents,
            "message": "Successfully found analysis summaries",
        }

        # Add the continuation token to the result if more files are available
        if response.get("IsTruncated"):
            result["continuationToken"] = response.get("NextContinuationToken")

        return {
            "statusCode": 200,
            "body": json.dumps(result),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"message": "Error fetching JSON files", "error": str(e)}
            ),
        }


if __name__ == "__main__":
    logger.info(lambda_handler({}, None))
