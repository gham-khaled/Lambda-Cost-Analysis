"""API endpoint to list Lambda functions in AWS account."""

import json
import logging
from typing import Any

import boto3
from api.cors_decorator import cors_header

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = boto3.client("lambda")


def fetch_lambda_function(marker: str | None = None) -> list[dict[str, Any]]:
    """
    Fetch Lambda functions with pagination support.

    Parameters
    ----------
    marker : str, optional
        Pagination marker

    Returns
    -------
    list of dict
        Lambda function details
    """
    response = (
        client.list_functions(Marker=marker) if marker else client.list_functions()
    )
    functions = []
    for function in response["Functions"]:
        functions.append(
            {
                "FunctionName": function["FunctionName"],
                "Runtime": function.get("Runtime", "Docker Image"),
                "PackageType": function["PackageType"],
                "Architectures": function["Architectures"],
                "MemorySize": function["MemorySize"],
                "LastModified": function["LastModified"],
            }
        )

    if "NextMarker" in response:
        return functions + fetch_lambda_function(response["NextMarker"])

    return functions


lambda_functions = fetch_lambda_function()


# TODO: Add more information in the response body
@cors_header  # type: ignore[misc]
def lambda_handler(event: Any, context: Any) -> dict[str, Any]:
    """
    List all Lambda functions in the AWS account.

    Parameters
    ----------
    event : Any
        Lambda event
    context : Any
        Lambda context

    Returns
    -------
    dict
        API Gateway response with Lambda functions list
    """
    #     parameters = event['queryStringParameters']
    #     selected_runtimes = parameters['selectedRuntime']
    #     selected_package_type = parameters['selectedPackageType']
    #     selected_architecture = parameters['selectedArchitecture']

    return {
        "statusCode": 200,
        "body": json.dumps(lambda_functions),
    }


if __name__ == "__main__":
    logger.info(lambda_handler(None, None))
