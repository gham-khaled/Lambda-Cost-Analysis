import json
import os
import unittest

import boto3
import moto
from moto import mock_aws




@mock_aws
class TestAnalysisInitializer(unittest.TestCase):

    bucket_name = "test-bucket"

    def setUp(self):
        self.mock_aws = moto.mock_aws()
        self.mock_aws.start()
        s3 = boto3.resource("s3", region_name='eu-west-1')
        self.bucket = s3.Bucket(self.bucket_name)
        self.bucket.create(CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        os.environ['BUCKET_NAME'] = self.bucket_name

    def tearDown(self):
        self.mock_aws.stop()

    def test_report_json_created(self):
        """
        Testing that the report json has been created with the Running Status
        """
        from utils.s3_utils import download_from_s3, upload_file_to_s3

        report_id = "test_report"
        event = {
            "lambda_functions_name": [{}],
            "report_id": report_id
        }

        from step_function.analysis_initializer import lambda_handler
        lambda_handler(event, None)
        report = json.loads(download_from_s3('summary.json', bucket_name=self.bucket_name, directory=report_id))
        self.assertDictEqual(report, {'status': 'Running'})
