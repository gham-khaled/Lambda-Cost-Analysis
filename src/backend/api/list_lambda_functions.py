"""API endpoint to list Lambda functions in AWS account."""

from typing import Any

import boto3
from aws_lambda_powertools import Logger

from backend.api.app import app

logger = Logger()

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


@app.get("/lambda-functions")  # type: ignore[misc]
def list_functions() -> list[dict[str, Any]]:
    """List all Lambda functions in the AWS account."""
    # TODO: Add filtering support
    # query_params = app.current_event.query_string_parameters or {}
    # selected_runtimes = query_params.get('selectedRuntime', [])
    # selected_package_type = query_params.get('selectedPackageType', [])
    # selected_architecture = query_params.get('selectedArchitecture', [])

    lambda_functions = fetch_lambda_function()
    logger.info("Listing Lambda functions", extra={"count": len(lambda_functions)})
    return lambda_functions


# Lambda handler is in app.py - this module just registers routes
