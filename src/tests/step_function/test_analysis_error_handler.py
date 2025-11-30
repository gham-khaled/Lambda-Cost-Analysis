"""Unit tests for analysis_error_handler Lambda function."""

import json
import os
from datetime import datetime

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


@pytest.fixture
def s3_bucket(aws_credentials):
    """Create a mocked S3 bucket."""
    bucket_name = "test-bucket"
    with mock_aws():
        s3 = boto3.resource("s3", region_name="us-east-1")
        bucket = s3.Bucket(bucket_name)
        bucket.create()
        os.environ["BUCKET_NAME"] = bucket_name
        yield bucket_name


@mock_aws
def test_error_handler_with_complete_error_details(s3_bucket, lambda_context):
    """Test error handler correctly processes complete error details."""
    from backend.step_function.analysis_error_handler import lambda_handler
    from backend.utils.s3_utils import download_from_s3

    report_id = "test-report-123"
    error_code = "States.TaskFailed"
    error_cause = "Lambda function execution failed"

    event = {
        "report_id": report_id,
        "error": error_code,
        "cause": error_cause,
    }

    response = lambda_handler(event, lambda_context)

    # Verify response structure
    assert response["status"] == "Failed"
    assert response["reportID"] == report_id
    assert response["error_code"] == error_code

    # Verify error summary was written to S3
    summary_json = download_from_s3(
        "summary.json", bucket_name=s3_bucket, directory=report_id
    )
    error_summary = json.loads(summary_json)

    assert error_summary["status"] == "Failed"
    assert error_summary["reportID"] == report_id
    assert error_summary["errorCode"] == error_code
    assert error_summary["errorMessage"] == error_cause
    assert "failureTime" in error_summary
    # Verify failureTime is a valid ISO format datetime string
    datetime.fromisoformat(error_summary["failureTime"])


@mock_aws
def test_error_handler_with_nested_error_output(s3_bucket, lambda_context):
    """Test error handler extracts report_id from nested error_output."""
    from backend.step_function.analysis_error_handler import lambda_handler
    from backend.utils.s3_utils import download_from_s3

    report_id = "test-report-456"
    error_code = "States.Runtime"
    error_cause = "Runtime error occurred"

    event = {
        "error_output": {"report_id": report_id},
        "error": error_code,
        "cause": error_cause,
    }

    response = lambda_handler(event, lambda_context)

    assert response["reportID"] == report_id

    # Verify file was written to correct directory
    summary_json = download_from_s3(
        "summary.json", bucket_name=s3_bucket, directory=report_id
    )
    error_summary = json.loads(summary_json)
    assert error_summary["reportID"] == report_id


@mock_aws
def test_error_handler_with_missing_error_details(s3_bucket, lambda_context):
    """Test error handler uses default values when error details are missing."""
    from backend.step_function.analysis_error_handler import lambda_handler
    from backend.utils.s3_utils import download_from_s3

    report_id = "test-report-789"

    event = {
        "report_id": report_id,
        # Missing "error" and "cause" fields
    }

    response = lambda_handler(event, lambda_context)

    assert response["status"] == "Failed"
    assert response["reportID"] == report_id
    assert response["error_code"] == "Unknown"

    # Verify defaults were used in S3 file
    summary_json = download_from_s3(
        "summary.json", bucket_name=s3_bucket, directory=report_id
    )
    error_summary = json.loads(summary_json)

    assert error_summary["errorCode"] == "Unknown"
    assert error_summary["errorMessage"] == "Unknown error occurred"


@mock_aws
def test_error_handler_with_missing_report_id(s3_bucket, lambda_context):
    """Test error handler handles missing report_id gracefully."""
    from backend.step_function.analysis_error_handler import lambda_handler

    error_code = "States.TaskFailed"
    error_cause = "Lambda function execution failed"

    event = {
        "error": error_code,
        "cause": error_cause,
        # Missing report_id in both root and error_output
    }

    response = lambda_handler(event, lambda_context)

    assert response["status"] == "Failed"
    assert response["reportID"] is None
    assert response["error_code"] == error_code


@mock_aws
def test_error_handler_partial_error_details(s3_bucket, lambda_context):
    """Test error handler with only error code missing."""
    from backend.step_function.analysis_error_handler import lambda_handler
    from backend.utils.s3_utils import download_from_s3

    report_id = "test-report-partial"
    error_cause = "Specific error message"

    event = {
        "report_id": report_id,
        "cause": error_cause,
        # Missing "error" field
    }

    response = lambda_handler(event, lambda_context)

    assert response["error_code"] == "Unknown"

    summary_json = download_from_s3(
        "summary.json", bucket_name=s3_bucket, directory=report_id
    )
    error_summary = json.loads(summary_json)

    assert error_summary["errorCode"] == "Unknown"
    assert error_summary["errorMessage"] == error_cause