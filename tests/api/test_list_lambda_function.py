import json
import os

import boto3
import pytest
from moto import mock_aws

# Moto does not mock Architecture/Package Options parameters when lambda creation --> Cannot create addition tests


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def lambda_functions(aws_credentials):
    """Create mock Lambda functions for testing."""
    with mock_aws():
        iam_client = boto3.client("iam", region_name="us-east-1")

        # Create a mock role
        role_response = iam_client.create_role(
            RoleName="mock-role",
            AssumeRolePolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
        )
        role_arn = role_response["Role"]["Arn"]

        client = boto3.client("lambda", region_name="us-east-1")

        functions = [
            {
                "FunctionName": "mock_function_1",
                "Runtime": "python3.8",
                "Role": role_arn,
                "Handler": "lambda_function.lambda_handler",
                "Code": {
                    "ZipFile": b"def lambda_handler(event, context):\n    return {'statusCode': 200, 'body': json.dumps('Hello from Lambda!')}"
                },
                "Description": "Mock Lambda function 1",
                "Timeout": 3,
                "MemorySize": 128,
            },
            {
                "FunctionName": "mock_function_2",
                "Runtime": "python3.9",
                "Role": role_arn,
                "Handler": "lambda_function.lambda_handler",
                "Code": {
                    "ZipFile": b"def lambda_handler(event, context):\n    return {'statusCode': 200, 'body': json.dumps('Hello from Lambda!')}"
                },
                "Description": "Mock Lambda function 2",
                "Timeout": 3,
                "MemorySize": 128,
                "Architectures": ["arm64"],
            },
            {
                "FunctionName": "mock_function_3",
                "Runtime": "dotnet7",
                "Role": role_arn,
                "Handler": "lambda_function.lambda_handler",
                "Code": {
                    "ZipFile": b"def lambda_handler(event, context):\n    return {'statusCode': 200, 'body': json.dumps('Hello from Lambda!')}"
                },
                "Description": "Mock Lambda function 3",
                "Timeout": 3,
                "MemorySize": 128,
            },
        ]

        # Create the Lambda functions
        for function in functions:
            client.create_function(
                FunctionName=function["FunctionName"],
                Runtime=function["Runtime"],
                Role=function["Role"],
                Handler=function["Handler"],
                Code=function["Code"],
                Description=function["Description"],
                Timeout=function["Timeout"],
                MemorySize=function["MemorySize"],
            )

        yield


@mock_aws
def test_successful_list_all_function(lambda_functions):
    """Test that the Lambda function successfully retrieves all functions."""
    from backend.api.list_lambda_functions import lambda_handler

    parameters = {
        "selectedRuntime": [
            "nodejs20.x",
            "nodejs18.x",
            "nodejs16.x",
            "python3.12",
            "python3.11",
            "python3.10",
            "python3.9",
            "python3.8",
            "java21",
            "java17",
            "java11",
            "java8.al2",
            "dotnet8",
            "dotnet7",
            "dotnet6",
            "ruby3.3",
            "ruby3.2",
            "custom",
        ],
        "selectedPackageType": ["Zip", "Image"],
        "selectedArchitecture": ["x86_64", "arm64"],
    }

    response = lambda_handler({"queryStringParameters": parameters}, None)
    response_functions = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert len(response_functions) == 3

    expected_response = [
        {
            "FunctionName": "mock_function_1",
            "Runtime": "python3.8",
            "PackageType": "Zip",
            "Architectures": ["x86_64"],
            "MemorySize": 128,
        },
        {
            "FunctionName": "mock_function_2",
            "Runtime": "python3.9",
            "PackageType": "Zip",
            "Architectures": ["x86_64"],
            "MemorySize": 128,
        },
        {
            "FunctionName": "mock_function_3",
            "Runtime": "dotnet7",
            "PackageType": "Zip",
            "Architectures": ["x86_64"],
            "MemorySize": 128,
        },
    ]

    for lambda_function in response_functions:
        del lambda_function["LastModified"]

    assert sorted(response_functions, key=lambda x: x["FunctionName"]) == sorted(
        expected_response, key=lambda x: x["FunctionName"]
    )


@pytest.mark.skip(reason="Moto limitation with Architecture parameter")
@mock_aws
def test_runtime_filter(lambda_functions):
    """Test that the Lambda function successfully filters by runtime."""
    from backend.api.list_lambda_functions import lambda_handler

    parameters = {
        "selectedRuntime": [
            "python3.9",
            "python3.8",
        ],
        "selectedPackageType": ["Zip", "Image"],
        "selectedArchitecture": ["x86_64", "arm64"],
    }

    response = lambda_handler({"queryStringParameters": parameters}, None)
    response_functions = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert len(response_functions) == 2

    expected_response = [
        {
            "FunctionName": "mock_function_1",
            "Runtime": "python3.8",
            "PackageType": "Zip",
            "Architectures": ["x86_64"],
            "MemorySize": 128,
        },
        {
            "FunctionName": "mock_function_2",
            "Runtime": "python3.9",
            "PackageType": "Zip",
            "Architectures": ["x86_64"],
            "MemorySize": 128,
        },
    ]

    for lambda_function in response_functions:
        del lambda_function["LastModified"]

    assert sorted(response_functions, key=lambda x: x["FunctionName"]) == sorted(
        expected_response, key=lambda x: x["FunctionName"]
    )
