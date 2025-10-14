import json
import os
import pytest
import boto3
from moto import mock_aws


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def s3_bucket(aws_credentials):
    """Create a mocked S3 bucket."""
    bucket_name = "test-bucket"
    with mock_aws():
        s3 = boto3.resource("s3", region_name='eu-west-1')
        bucket = s3.Bucket(bucket_name)
        bucket.create(CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        os.environ['BUCKET_NAME'] = bucket_name
        yield bucket_name


@mock_aws
def test_successful_file_retrieval(s3_bucket):
    """Test that the Lambda function successfully retrieves a file from S3."""
    from utils.s3_utils import upload_file_to_s3
    from api.get_analysis_report import lambda_handler

    sample_report_id = "sample.json"
    sample_content = {"status": "Completed"}
    upload_file_to_s3(json.dumps(sample_content), 'summary.json', s3_bucket, sample_report_id)
    upload_file_to_s3(json.dumps(sample_content), 'analysis.csv', s3_bucket, sample_report_id)
    event = {
        "queryStringParameters": {
            "reportID": sample_report_id
        }
    }

    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['summary'] == sample_content


@mock_aws
def test_file_not_found(s3_bucket):
    """Test that the Lambda function returns an error when the file is not found."""
    from api.get_analysis_report import lambda_handler

    event = {
        "queryStringParameters": {
            "reportID": "nonexistent.json"
        }
    }

    response = lambda_handler(event, None)
    assert response['statusCode'] == 404
    assert json.loads(response['body']) == {"error": "Analysis does not exists or have been deleted", 'status': 'Error'}


@mock_aws
def test_missing_filename_parameter(s3_bucket):
    """Test that the Lambda function returns an error when the filename parameter is missing."""
    from api.get_analysis_report import lambda_handler

    event = {
        "queryStringParameters": {}
    }

    response = lambda_handler(event, None)
    assert response['statusCode'] == 400
    assert json.loads(response['body']) == {"error": "Report ID parameter is required"}
