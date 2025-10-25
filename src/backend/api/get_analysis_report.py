"""API endpoint to retrieve analysis report by ID."""

import json
import os
from io import StringIO
from typing import Any

import boto3
import pandas as pd
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from botocore.exceptions import ClientError

from backend.api.app import app
from backend.utils.s3_utils import download_from_s3

logger = Logger()

s3_client = boto3.client("s3")

bucket_name = os.environ["BUCKET_NAME"]


@app.get("/report")  # type: ignore[misc]
def get_report() -> dict[str, Any]:
    """Retrieve analysis report by report ID."""
    query_params = app.current_event.query_string_parameters or {}
    report_id = query_params.get("reportID")

    if not report_id:
        raise NotFoundError("Report ID parameter is required")

    try:
        # Fetch the S3 object
        summary_str = download_from_s3(
            file_name="summary.json", bucket_name=bucket_name, directory=report_id
        )
        summary: dict[str, Any] = json.loads(summary_str)

        logger.info(
            "Retrieved analysis report",
            extra={"report_id": report_id, "status": summary.get("status")},
        )

        if summary["status"] in ["Running", "Error"]:
            return {"summary": summary}
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
                "analysis": json.loads(df.to_json(orient="records")),
                "summary": summary,
                "url": download_url,
            }
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise NotFoundError("Analysis does not exist or has been deleted")
        else:
            logger.exception(
                "Error retrieving analysis report", extra={"report_id": report_id}
            )
            raise


# Lambda handler is in app.py - this module just registers routes
