"""API endpoint to retrieve analysis report by ID."""

import json
import logging
import os
from io import StringIO
from typing import Any

import boto3
import pandas as pd
from botocore.exceptions import ClientError

from backend.api.cors_decorator import cors_header
from backend.utils.s3_utils import download_from_s3

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

bucket_name = os.environ["BUCKET_NAME"]


@cors_header
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Retrieve analysis report by report ID.

    Parameters
    ----------
    event : dict
        Lambda event with reportID query parameter
    context : Any
        Lambda context

    Returns
    -------
    dict
        API Gateway response with analysis data and download URL
    """
    report_id = event.get("queryStringParameters", {}).get("reportID")

    if not report_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Report ID parameter is required"}),
        }

    try:
        # Fetch the S3 object
        summary_str = download_from_s3(
            file_name="summary.json", bucket_name=bucket_name, directory=report_id
        )
        summary: dict[str, Any] = json.loads(summary_str)
        if summary["status"] in ["Running", "Error"]:
            return {
                "statusCode": 200,
                "body": json.dumps({"summary": summary}),
            }
        else:
            analysis = download_from_s3(
                file_name="analysis.csv", bucket_name=bucket_name, directory=report_id
            )

            download_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": f"{report_id}/analysis.csv"},
                ExpiresIn=3600,
            )
            df = pd.read_csv(StringIO(analysis), sep=",", index_col=0)
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "analysis": json.loads(df.to_json(orient="records")),
                        "summary": summary,
                        "url": download_url,
                    }
                ),
            }
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return {
                "statusCode": 404,
                "body": json.dumps(
                    {
                        "error": "Analysis does not exists or have been deleted",
                        "status": "Error",
                    }
                ),
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e), "status": "Error"}),
            }


if __name__ == "__main__":
    event = {"queryStringParameters": {"reportID": "running"}}
    result = lambda_handler(event, None)
    logger.info(result)
    logger.info(json.loads(result["body"]))
