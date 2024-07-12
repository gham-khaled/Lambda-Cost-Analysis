import json
import os
import unittest
import boto3

# Assuming your Lambda function code is in a file named `lambda_function.py`
import moto
from moto import mock_aws


@mock_aws
class TestGetAnalysisReport(unittest.TestCase):
    bucket_name = "test-bucket"

    def setUp(self):
        self.mock_aws = moto.mock_aws()
        self.mock_aws.start()
        s3 = boto3.resource("s3", region_name='eu-west-1')
        self.bucket = s3.Bucket(self.bucket_name)
        self.bucket.create(CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        os.environ['BUCKET_NAME'] = self.bucket_name

        # Adding a sample JSON file to the bucket

    def tearDown(self):
        self.mock_aws.stop()

    def test_successful_file_retrieval(self):
        """
        Test that the Lambda function successfully retrieves a file from S3.
        """
        from utils.s3_utils import upload_file_to_s3

        sample_report_id = "sample.json"
        sample_content = {"status": "Completed"}
        upload_file_to_s3(json.dumps(sample_content), 'summary.json', self.bucket_name, sample_report_id)
        upload_file_to_s3(json.dumps(sample_content), 'analysis.csv', self.bucket_name, sample_report_id)
        event = {
            "queryStringParameters": {
                "reportID": sample_report_id
            }
        }
        from api.get_analysis_report import lambda_handler
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['summary'], sample_content)

    def test_file_not_found(self):
        """
        Test that the Lambda function returns an error when the file is not found.
        """
        event = {
            "queryStringParameters": {
                "reportID": "nonexistent.json"
            }
        }
        from api.get_analysis_report import lambda_handler
        response = lambda_handler(event, None)
        print(response)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']),
                         {"error": "Analysis does not exists or have been deleted", 'status': 'Error'})

    def test_missing_filename_parameter(self):
        """
        Test that the Lambda function returns an error when the filename parameter is missing.
        """
        event = {
            "queryStringParameters": {}
        }
        from api.get_analysis_report import lambda_handler
        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), {"error": "Report ID parameter is required"})


if __name__ == '__main__':
    unittest.main()
