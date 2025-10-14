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
def test_no_file_found(s3_bucket):
    """Testing the right response when no file is found."""
    from api.historical_analysis_report import lambda_handler

    response = lambda_handler({}, None)
    response_body = json.loads(response['body'])
    assert response_body == {'message': 'No files found.'}


@mock_aws
def test_function_succeeding(s3_bucket):
    """Testing that the S3 object summaries will be returned correctly if found."""
    from utils.s3_utils import upload_file_to_s3
    from api.historical_analysis_report import lambda_handler

    prefix_name = 'summaries'
    json_load_1 = {"status": "Completed", "allDurationInSeconds": 249.003, "avgprovisionedMemoryMB": 152.587875,
                   "MemoryCost": 0.000783477,
                   "InvocationCost": 0.0000116, "totalCost": 0.000795077, "avgCostPerInvocation": 0.000146568,
                   "avgmaxMemoryUsedMB": 92.5064, "avgoverProvisionedMB": 60.081475,
                   "optimalTotalCost": 0.000382066, "potentialSavings": 0.0004128712,
                   "avgDurationPerInvocation": 37.33415}
    json_load_2 = {"status": "Completed", "allDurationInSeconds": 500.003, "avgprovisionedMemoryMB": 300.587875,
                   "MemoryCost": 0.000783477,
                   "InvocationCost": 0.0000116, "totalCost": 0.000795077, "avgCostPerInvocation": 0.000146568,
                   "avgmaxMemoryUsedMB": 92.5064, "avgoverProvisionedMB": 60.081475,
                   "optimalTotalCost": 0.000382066, "potentialSavings": 0.0004128712,
                   "avgDurationPerInvocation": 37.33415}
    upload_file_to_s3(json.dumps(json_load_1), 'json_load_1.json', s3_bucket, prefix_name)
    upload_file_to_s3(json.dumps(json_load_2), 'json_load_2.json', s3_bucket, prefix_name)

    response = lambda_handler({}, None)
    response_body = json.loads(response['body'])
    file_content = response_body['jsonContents']

    assert len(file_content) == 2
    assert file_content == [json_load_1, json_load_2]


@mock_aws
def test_function_pagination(s3_bucket):
    """Testing that the pagination is working correctly."""
    from utils.s3_utils import upload_file_to_s3
    from api.historical_analysis_report import lambda_handler

    prefix_name = 'summaries'
    json_load_1 = {"status": "Completed", "allDurationInSeconds": 249.003, "avgprovisionedMemoryMB": 152.587875,
                   "MemoryCost": 0.000783477,
                   "InvocationCost": 0.0000116, "totalCost": 0.000795077, "avgCostPerInvocation": 0.000146568,
                   "avgmaxMemoryUsedMB": 92.5064, "avgoverProvisionedMB": 60.081475,
                   "optimalTotalCost": 0.000382066, "potentialSavings": 0.0004128712,
                   "avgDurationPerInvocation": 37.33415}
    for i in range(12):
        upload_file_to_s3(json.dumps(json_load_1), f'json_load_{i}.json', s3_bucket, prefix_name)

    response = lambda_handler({'queryStringParameters': {'rowsPerPage': "10"}}, None)
    response_body = json.loads(response['body'])
    file_content = response_body['jsonContents']
    assert len(file_content) == 10
    assert 'continuationToken' in response_body

    parameters = {'continuationToken': response_body['continuationToken'], 'rowsPerPage': "10"}
    response = lambda_handler({'queryStringParameters': parameters}, None)
    response_body = json.loads(response['body'])
    file_content = response_body['jsonContents']
    assert len(file_content) == 2
