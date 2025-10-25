import os
from datetime import datetime, timedelta
from unittest.mock import patch

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["BUCKET_NAME"] = ""


@pytest.fixture
def mock_query_results():
    """Sample CloudWatch Logs Insights query results."""
    return {
        "status": "Complete",
        "results": [
            [
                {"field": "timeoutInvocations", "value": "1"},
                {"field": "countInvocations", "value": "3"},
                {"field": "memoryExceededInvocation", "value": "0"},
                {"field": "singleInvocationCost", "value": "0.0000002"},
                {"field": "GBSecondMemoryPrice", "value": "0.0000166667"},
                {"field": "GBSecondStoragePrice", "value": "0.0000000309"},
                {"field": "StorageSizeMB", "value": "0"},
                {"field": "provisionedMemoryMB", "value": "128"},
                {"field": "allDurationInSeconds", "value": "3.0"},
                {"field": "GbSecondsMemoryConsumed", "value": "0.375"},
                {"field": "GbSecondsStorageConsumed", "value": "0"},
                {"field": "MemoryCost", "value": "0.00000625"},
                {"field": "StorageCost", "value": "0"},
                {"field": "InvocationCost", "value": "0.0000006"},
                {"field": "totalCost", "value": "0.00000685"},
                {"field": "maxMemoryUsedMB", "value": "70"},
                {"field": "overProvisionedMB", "value": "58"},
                {"field": "optimalMinMemory", "value": "84.0"},
                {"field": "optimalMemory", "value": "84.0"},
                {"field": "optimalMemoryCost", "value": "0.000004101563"},
                {"field": "potentialSavings", "value": "0.000002148438"},
                {"field": "avgCostPerInvocation", "value": "0.00000228333"},
                {"field": "avgDurationPerInvocation", "value": "1.0"},
            ]
        ],
    }


@mock_aws
def test_moto_supports_cloudwatch_insights():
    """Test that moto now supports CloudWatch Logs Insights API calls."""
    logs_client = boto3.client("logs", region_name="us-east-1")
    log_group_name = "/aws/lambda/test_lambda"

    # Create log group
    logs_client.create_log_group(logGroupName=log_group_name)

    now = datetime.now()

    try:
        # Test that start_query is supported
        query_id = logs_client.start_query(
            logGroupName=log_group_name,
            startTime=int((now - timedelta(days=1)).timestamp()),
            endTime=int(now.timestamp()),
            queryString="fields @timestamp, @message | limit 20",
        )

        assert "queryId" in query_id, "Moto should support start_query"

        # Test that get_query_results is supported
        result = logs_client.get_query_results(queryId=query_id["queryId"])
        assert "status" in result, "Moto should support get_query_results"
        assert result["status"] == "Complete", "Query should complete"

    except Exception as e:
        pytest.skip(f"Moto doesn't support CloudWatch Logs Insights yet: {str(e)}")


@mock_aws
@patch("backend.step_function.analysis_generator.cloudwatch_client")
@patch("backend.step_function.analysis_generator.lambda_client")
def test_get_lambda_cost_full_logic(
    mock_lambda_client, mock_cloudwatch_client, mock_query_results, aws_credentials
):
    """Test the full get_lambda_cost function logic with mocked AWS responses."""
    from backend.step_function.analysis_generator import get_lambda_cost

    # Mock Lambda function configuration
    mock_lambda_client.get_function_configuration.return_value = {
        "Runtime": "python3.12",
        "MemorySize": 128,
        "Architectures": ["x86_64"],
        "EphemeralStorage": {"Size": 512},
        "LoggingConfig": {"LogGroup": "/aws/lambda/test_lambda"},
    }

    # Mock log group exists
    mock_cloudwatch_client.describe_log_groups.return_value = {
        "logGroups": [{"logGroupName": "/aws/lambda/test_lambda"}]
    }

    # Mock start_query
    mock_cloudwatch_client.start_query.return_value = {"queryId": "test-query-id-12345"}

    # Mock get_query_results with realistic data
    mock_cloudwatch_client.get_query_results.return_value = mock_query_results

    # Call the function
    start_date = "2024-01-01T00:00:00.000Z"
    end_date = "2024-01-31T23:59:59.999Z"

    result = get_lambda_cost("test_lambda", start_date, end_date)

    # Verify the result structure
    assert result is not None, "Should return a result"
    assert result["functionName"] == "test_lambda"
    assert result["runtime"] == "python3.12"
    assert result["architecture"] == "x86_64"

    # Verify cost analysis fields
    assert float(result["countInvocations"]) == 3
    assert float(result["timeoutInvocations"]) == 1
    assert float(result["memoryExceededInvocation"]) == 0
    assert float(result["provisionedMemoryMB"]) == 128
    assert float(result["maxMemoryUsedMB"]) == 70
    assert float(result["overProvisionedMB"]) == 58
    assert float(result["optimalMemory"]) == 84.0
    assert float(result["totalCost"]) > 0
    assert float(result["potentialSavings"]) > 0
    assert float(result["avgDurationPerInvocation"]) == 1.0

    # Verify Lambda client was called correctly
    mock_lambda_client.get_function_configuration.assert_called_once_with(
        FunctionName="test_lambda"
    )

    # Verify CloudWatch Logs query was executed
    mock_cloudwatch_client.start_query.assert_called_once()
    mock_cloudwatch_client.get_query_results.assert_called_once_with(
        queryId="test-query-id-12345"
    )


@mock_aws
@patch("backend.step_function.analysis_generator.cloudwatch_client")
@patch("backend.step_function.analysis_generator.lambda_client")
def test_get_lambda_cost_no_log_group(
    mock_lambda_client, mock_cloudwatch_client, aws_credentials
):
    """Test get_lambda_cost when log group doesn't exist."""
    from backend.step_function.analysis_generator import get_lambda_cost

    # Mock Lambda function configuration
    mock_lambda_client.get_function_configuration.return_value = {
        "Runtime": "python3.12",
        "MemorySize": 128,
        "Architectures": ["x86_64"],
        "EphemeralStorage": {"Size": 512},
        "LoggingConfig": {"LogGroup": "/aws/lambda/nonexistent"},
    }

    # Mock log group doesn't exist
    mock_cloudwatch_client.describe_log_groups.return_value = {"logGroups": []}

    start_date = "2024-01-01T00:00:00.000Z"
    end_date = "2024-01-31T23:59:59.999Z"

    result = get_lambda_cost("test_lambda", start_date, end_date)

    # Should return None when log group doesn't exist
    assert result is None


@mock_aws
@patch("backend.step_function.analysis_generator.cloudwatch_client")
@patch("backend.step_function.analysis_generator.lambda_client")
def test_get_lambda_cost_no_invocations(
    mock_lambda_client, mock_cloudwatch_client, aws_credentials
):
    """Test get_lambda_cost when there are no invocations."""
    from backend.step_function.analysis_generator import get_lambda_cost

    # Mock Lambda function configuration
    mock_lambda_client.get_function_configuration.return_value = {
        "Runtime": "python3.12",
        "MemorySize": 256,
        "Architectures": ["arm64"],
        "EphemeralStorage": {"Size": 1024},
        "LoggingConfig": {"LogGroup": "/aws/lambda/test_lambda"},
    }

    # Mock log group exists
    mock_cloudwatch_client.describe_log_groups.return_value = {
        "logGroups": [{"logGroupName": "/aws/lambda/test_lambda"}]
    }

    # Mock start_query
    mock_cloudwatch_client.start_query.return_value = {"queryId": "test-query-id-67890"}

    # Mock get_query_results with no results
    mock_cloudwatch_client.get_query_results.return_value = {
        "status": "Complete",
        "results": [],
    }

    start_date = "2024-01-01T00:00:00.000Z"
    end_date = "2024-01-31T23:59:59.999Z"

    result = get_lambda_cost("test_lambda", start_date, end_date)

    # Should return None when there are no query results
    assert result is None
