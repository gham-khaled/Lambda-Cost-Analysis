import json
import os

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
        s3 = boto3.resource("s3", region_name="eu-west-1")
        bucket = s3.Bucket(bucket_name)
        bucket.create(CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})
        os.environ["BUCKET_NAME"] = bucket_name
        yield bucket_name


@mock_aws
def test_report_json_created(s3_bucket, lambda_context):
    """Testing that the report json has been created with the Running Status."""
    from backend.step_function.analysis_initializer import lambda_handler
    from backend.utils.s3_utils import download_from_s3

    report_id = "test_report"
    event = {"lambda_functions_name": [{}], "report_id": report_id}

    lambda_handler(event, lambda_context)
    report = json.loads(
        download_from_s3("summary.json", bucket_name=s3_bucket, directory=report_id)
    )
    assert report == {"status": "Running"}
