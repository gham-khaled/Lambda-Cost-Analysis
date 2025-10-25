"""Initialize Lambda cost analysis Step Function."""

import json
import os
from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from backend.utils.s3_utils import upload_file_to_s3
from backend.utils.sf_utils import upload_divided_params

logger = Logger()

bucket_name = os.environ["BUCKET_NAME"]
max_arn_per_invocation = 5


@logger.inject_lambda_context(log_event=True)  # type: ignore[misc]
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """
    Initialize cost analysis by creating report and dividing Lambda functions.

    Parameters
    ----------
    event : dict
        Step Function event with lambda_functions_name, report_id, start_date, end_date
    context : LambdaContext
        Lambda context object

    Returns
    -------
    dict
        Parameters for next step with divided Lambda functions
    """
    lambda_functions_name = event["lambda_functions_name"]

    report_id = event["report_id"]
    start_date = event.get("start_date")
    end_date = event.get("end_date")

    logger.info(
        "Initializing analysis",
        extra={"report_id": report_id, "num_functions": len(lambda_functions_name)},
    )

    upload_file_to_s3(
        body=json.dumps({"status": "Running"}),
        file_name="summary.json",
        bucket_name=bucket_name,
        directory=report_id,
    )
    sf_parameters = upload_divided_params(
        lambda_functions_name,
        divider=max_arn_per_invocation,
        bucket_name=bucket_name,
        directory_name="SF_PARAMS/SF_PARAMS",
    )

    logger.info("Analysis initialized", extra={"num_batches": len(sf_parameters)})

    return {
        "lambda_functions_name": sf_parameters,
        "start_date": start_date,
        "end_date": end_date,
        "report_id": report_id,
    }
