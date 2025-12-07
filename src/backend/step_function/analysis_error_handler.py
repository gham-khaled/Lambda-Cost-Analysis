"""Handle Step Function execution failures and store error details."""

import json
import os
from datetime import datetime
from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from backend.utils.s3_utils import upload_file_to_s3

logger = Logger()

bucket_name = os.environ["BUCKET_NAME"]


@logger.inject_lambda_context(log_event=True)  # type: ignore[misc]
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """
    Handle Step Function execution failures.

    Parameters
    ----------
    event : dict
        Step Function error event containing error info and report_id
    context : LambdaContext
        Lambda context object

    Returns
    -------
    dict
        Status confirmation
    """
    # Extract error information from Step Function
    error_output = event.get("error_output", {})
    report_id = error_output.get("report_id") or event.get("report_id")
    error_code = event.get("error", "Unknown")
    error_cause = event.get("cause", "Unknown error occurred")

    logger.error(
        "Step Function execution failed",
        extra={
            "report_id": report_id,
            "error_code": error_code,
            "error_cause": error_cause,
        },
    )

    # Create error summary
    error_summary = {
        "status": "Failed",
        "reportID": report_id,
        "errorCode": error_code,
        "errorMessage": error_cause,
        "failureTime": datetime.now().isoformat(),
    }

    # Upload error summary to S3
    try:
        upload_file_to_s3(
            body=json.dumps(error_summary),
            file_name="summary.json",
            bucket_name=bucket_name,
            directory=report_id,
        )
        logger.info("Error summary written to S3", extra={"report_id": report_id})
    except Exception as e:
        logger.exception(
            "Failed to write error summary to S3",
            extra={"report_id": report_id, "exception": str(e)},
        )

    return {"status": "Failed", "reportID": report_id, "error_code": error_code}
