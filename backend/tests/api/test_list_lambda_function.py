import json
import os
import unittest
import boto3

# Assuming your Lambda function code is in a file named `lambda_function.py`
import moto
from moto import mock_aws


# Moto does not mock Architecture/Package Options parameters when lambda creation --> Cannot create addition tests

@mock_aws
class TestGetAnalysisReport(unittest.TestCase):
    bucket_name = "test-bucket"

    def setUp(self):
        self.mock_aws = moto.mock_aws()
        self.mock_aws.start()
        iam_client = boto3.client('iam')

        # Create a mock role
        role_response = iam_client.create_role(
            RoleName='mock-role',
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
        )
        role_arn = role_response['Role']['Arn']

        client = boto3.client('lambda')

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
                "MemorySize": 128
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
                "Architectures": ['arm64']
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
                "MemorySize": 128
            }
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
                MemorySize=function["MemorySize"]
            )

    def tearDown(self):
        self.mock_aws.stop()

    def test_successful_list_all_function(self):
        """
        Test that the Lambda function successfully retrieves all functions
        """
        parameters = {
            "selectedRuntime": [
                'nodejs20.x',
                'nodejs18.x',
                'nodejs16.x',
                'python3.12',
                'python3.11',
                'python3.10',
                'python3.9',
                'python3.8',
                'java21',
                'java17',
                'java11',
                'java8.al2',
                'dotnet8',
                'dotnet7',
                'dotnet6',
                'ruby3.3',
                'ruby3.2',
                'custom'
            ],
            "selectedPackageType": ['Zip', 'Image'],
            "selectedArchitecture": ['x86_64', 'arm64']
        }
        from api.list_lambda_functions import lambda_handler
        response = lambda_handler({'queryStringParameters': parameters}, None)
        response_functions = json.loads(response['body'])
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(len(response_functions), 3)
        expected_response = [{"FunctionName": "mock_function_1", "Runtime": "python3.8", "PackageType": "Zip",
                              "Architectures": ["x86_64"], "MemorySize": 128},
                             {"FunctionName": "mock_function_2", "Runtime": "python3.9", "PackageType": "Zip",
                              "Architectures": ["x86_64"], "MemorySize": 128},
                             {"FunctionName": "mock_function_3", "Runtime": "dotnet7", "PackageType": "Zip",
                              "Architectures": ["x86_64"], "MemorySize": 128}]
        for lambda_function in response_functions:
            del lambda_function['LastModified']

        self.assertCountEqual(response_functions, expected_response)
    #
    # def test_runtime_filter(self):
    #     """
    #     Test that the Lambda function successfully retrieves all functions
    #     """
    #     parameters = {
    #         "selectedRuntime": [
    #             'python3.9',
    #             'python3.8',
    #         ],
    #         "selectedPackageType": ['Zip', 'Image'],
    #         "selectedArchitecture": ['x86_64', 'arm64']
    #     }
    #     from api.list_lambda_functions import lambda_handler
    #     response = lambda_handler({'queryStringParameters': parameters}, None)
    #     response_functions = json.loads(response['body'])
    #     self.assertEqual(response['statusCode'], 200)
    #     self.assertEqual(len(response_functions), 2)
    #     expected_response = [{"FunctionName": "mock_function_1", "Runtime": "python3.8", "PackageType": "Zip",
    #                           "Architectures": ["x86_64"], "MemorySize": 128},
    #                          {"FunctionName": "mock_function_2", "Runtime": "python3.9", "PackageType": "Zip",
    #                           "Architectures": ["x86_64"], "MemorySize": 128}]
    #     for lambda_function in response_functions:
    #         del lambda_function['LastModified']
    #
    #     self.assertCountEqual(response_functions, expected_response)


if __name__ == '__main__':
    unittest.main()
