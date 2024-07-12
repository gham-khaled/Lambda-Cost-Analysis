import json
import os
import unittest
import boto3
import moto
from moto import mock_aws


@mock_aws
class TestListAnalysisReport(unittest.TestCase):
    bucket_name = "test-bucket"
    prefix_name = 'summaries'

    def setUp(self):
        self.mock_aws = moto.mock_aws()
        self.mock_aws.start()
        s3 = boto3.resource("s3", region_name='eu-west-1')
        self.bucket = s3.Bucket(self.bucket_name)
        self.bucket.create(CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        os.environ['BUCKET_NAME'] = self.bucket_name

    def tearDown(self):
        self.mock_aws.stop()

    def test_no_file_found(self):
        """
        Testing the right response when no file is found
        """

        from api.historical_analysis_report import lambda_handler
        response = lambda_handler({}, None)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body, {'message': 'No files found.'})

    def test_function_succeeding(self):
        """
        Testing that the S3 object summaries will be returned correctly if found
        """
        from utils.s3_utils import upload_file_to_s3

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
        upload_file_to_s3(json.dumps(json_load_1), 'json_load_1.json', self.bucket_name, self.prefix_name, )
        upload_file_to_s3(json.dumps(json_load_2), 'json_load_2.json', self.bucket_name, self.prefix_name, )
        from api.historical_analysis_report import lambda_handler
        response = lambda_handler({}, None)
        response_body = json.loads(response['body'])
        file_content = response_body['jsonContents']

        self.assertEqual(len(file_content), 2)
        self.assertListEqual(file_content, [json_load_1, json_load_2])

    def test_function_pagination(self):
        """
        Testing that the pagination is working correctly
        """
        from utils.s3_utils import upload_file_to_s3

        json_load_1 = {"status": "Completed", "allDurationInSeconds": 249.003, "avgprovisionedMemoryMB": 152.587875,
                       "MemoryCost": 0.000783477,
                       "InvocationCost": 0.0000116, "totalCost": 0.000795077, "avgCostPerInvocation": 0.000146568,
                       "avgmaxMemoryUsedMB": 92.5064, "avgoverProvisionedMB": 60.081475,
                       "optimalTotalCost": 0.000382066, "potentialSavings": 0.0004128712,
                       "avgDurationPerInvocation": 37.33415}
        for i in range(12):
            upload_file_to_s3(json.dumps(json_load_1), f'json_load_{i}.json', self.bucket_name, self.prefix_name, )
        from api.historical_analysis_report import lambda_handler
        response = lambda_handler({'queryStringParameters': {'rowsPerPage': "10"}}, None)
        response_body = json.loads(response['body'])
        file_content = response_body['jsonContents']
        self.assertEqual(len(file_content), 10)
        self.assertTrue('continuationToken' in response_body)

        parameters = {'continuationToken': response_body['continuationToken'], 'rowsPerPage': "10"}
        response = lambda_handler({'queryStringParameters': parameters}, None)
        response_body = json.loads(response['body'])
        file_content = response_body['jsonContents']
        self.assertEqual(len(file_content), 2)
