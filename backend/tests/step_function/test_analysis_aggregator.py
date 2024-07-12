import csv
import json
import os
import unittest
from io import StringIO

import boto3
import moto
from moto import mock_aws



@mock_aws
class TestAnalysisAggregator(unittest.TestCase):
    bucket_name = "test-bucket"

    def setUp(self):
        self.mock_aws = moto.mock_aws()
        self.mock_aws.start()
        s3 = boto3.resource("s3")
        self.bucket = s3.Bucket(self.bucket_name)
        self.bucket.create(CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        os.environ['BUCKET_NAME'] = self.bucket_name

    def tearDown(self):
        self.mock_aws.stop()

    def write_csv_file(self, csv_dict_content):
        csv_buffer = StringIO()

        field_names = csv_dict_content[0].keys()

        # Write the data to the CSV file
        writer = csv.DictWriter(csv_buffer, fieldnames=field_names, extrasaction='ignore')
        writer.writeheader()  # Write the header row
        writer.writerows(csv_dict_content)  # Write the data rows
        return csv_buffer

    def test_file_merge(self):
        """
        Testing that the CSV files are merged correctly
        """
        from utils.s3_utils import download_from_s3, upload_file_to_s3

        report_id = 'test-report'
        start_date = 'X'
        end_date = 'X'
        directory = f'single_analysis/{report_id}'

        file1 = [
            {
                "functionName": "LambdaA",
                "runtime": "python3.10",
                "allDurationInSeconds": 21,
                "provisionedMemoryMB": 128,
                "MemoryCost": 1,
                "InvocationCost": 0.5,
                "totalCost": 1.5,
                "avgCostPerInvocation": 0.5,
                "maxMemoryUsedMB": 80,
                "overProvisionedMB": 48,
                "optimalMemory": 128,
                "optimalTotalCost": 1.5,
                "potentialSavings": 0,
                "avgDurationPerInvocation": 3,
                "memoryExceededInvocation": 0,
                "timeoutInvocations": 0
            }
        ]
        file2 = [
            {
                "functionName": "LambdaC",
                "runtime": "python3.10",
                "allDurationInSeconds": 21,
                "provisionedMemoryMB": 128,
                "MemoryCost": 1,
                "InvocationCost": 0.5,
                "totalCost": 1.5,
                "avgCostPerInvocation": 0.5,
                "maxMemoryUsedMB": 80,
                "overProvisionedMB": 48,
                "optimalMemory": 128,
                "optimalTotalCost": 1.5,
                "potentialSavings": 0,
                "avgDurationPerInvocation": 3,
                "memoryExceededInvocation": 0,
                "timeoutInvocations": 0
            }
        ]

        upload_file_to_s3(body=self.write_csv_file(file1).getvalue(), bucket_name=self.bucket_name,
                          file_name='file1.csv',
                          directory=directory)
        upload_file_to_s3(body=self.write_csv_file(file2).getvalue(), bucket_name=self.bucket_name,
                          file_name='file2.csv',
                          directory=directory)
        from step_function.analysis_aggregator import lambda_handler
        event = [
            {
                "filename": "file1.csv",
                "bucket": self.bucket_name,
                "directory": directory,
                "report_id": report_id,
                "start_date": start_date,
                "end_date": end_date
            }
            , {
                "filename": "file2.csv",
                "bucket": self.bucket_name,
                "directory": directory,
                "report_id": report_id,
                "start_date": start_date,
                "end_date": end_date
            }
        ]
        lambda_handler(event, None)
        csv_body = download_from_s3('analysis.csv', self.bucket_name, report_id)
        csv_file = StringIO(csv_body)

        # Use the csv.DictReader to read the CSV file and convert it to a list of dictionaries
        reader = csv.DictReader(csv_file)
        data_list = [dict(row) for row in reader]
        for data in data_list:
            del data['']
        files_merge = file1 + file2
        for file in files_merge:
            for key, value in list(file.items()):
                file[key] = str(value)

        files_merge = sorted(files_merge, key=lambda x: x['functionName'])
        data_list = sorted(data_list, key=lambda x: x['functionName'])

        self.assertEqual(len(data_list), 2)
        self.assertCountEqual(data_list, files_merge)

    def test_summary_file(self):
        """
        Testing that the CSV files are merged correctly
        """
        from utils.s3_utils import download_from_s3, upload_file_to_s3

        report_id = 'test-report'
        directory = f'single_analysis/{report_id}'
        start_date = 'X'
        end_date = 'X'
        file1 = [
            {
                "functionName": "LambdaA",
                "runtime": "python3.10",
                "allDurationInSeconds": 21,
                "provisionedMemoryMB": 128,
                "MemoryCost": 1,
                "InvocationCost": 0.5,
                "totalCost": 1.5,
                "avgCostPerInvocation": 0.5,
                "maxMemoryUsedMB": 80,
                "overProvisionedMB": 48,
                "optimalMemory": 128,
                "optimalTotalCost": 1.5,
                "potentialSavings": 0,
                "avgDurationPerInvocation": 3,
                "memoryExceededInvocation": 5,
                "timeoutInvocations": 2
            }
            , {
                "functionName": "LambdaB",
                "runtime": "python3.10",
                "allDurationInSeconds": 55,
                "provisionedMemoryMB": 256,
                "MemoryCost": 2,
                "InvocationCost": 0.5,
                "totalCost": 2.5,
                "avgCostPerInvocation": 0.75,
                "maxMemoryUsedMB": 144,
                "overProvisionedMB": 112,
                "optimalMemory": 166,
                "optimalTotalCost": 2,
                "potentialSavings": 0.5,
                "avgDurationPerInvocation": 3,
                "memoryExceededInvocation": 0,
                "timeoutInvocations": 1
            }
        ]
        file2 = [
            {
                "functionName": "LambdaC",
                "runtime": "python3.10",
                "allDurationInSeconds": 21,
                "provisionedMemoryMB": 128,
                "MemoryCost": 1,
                "InvocationCost": 0.5,
                "totalCost": 1.5,
                "avgCostPerInvocation": 0.5,
                "maxMemoryUsedMB": 80,
                "overProvisionedMB": 48,
                "optimalMemory": 128,
                "optimalTotalCost": 1.5,
                "potentialSavings": 0,
                "avgDurationPerInvocation": 3,
                "memoryExceededInvocation": 0,
                "timeoutInvocations": 0
            }
        ]

        upload_file_to_s3(body=self.write_csv_file(file1).getvalue(), bucket_name=self.bucket_name,
                          file_name='file1.csv',
                          directory=directory)
        upload_file_to_s3(body=self.write_csv_file(file2).getvalue(), bucket_name=self.bucket_name,
                          file_name='file2.csv',
                          directory=directory)
        from step_function.analysis_aggregator import lambda_handler
        event = [
            {
                "filename": "file1.csv",
                "bucket": self.bucket_name,
                "directory": directory,
                "report_id": report_id,
                "start_date": start_date,
                "end_date": end_date
            }
            , {
                "filename": "file2.csv",
                "bucket": self.bucket_name,
                "directory": directory,
                "report_id": report_id,
                "start_date": start_date,
                "end_date": end_date
            }
        ]
        lambda_handler(event, None)
        report = json.loads(download_from_s3('summary.json', bucket_name=self.bucket_name, directory=report_id))
        print(report)
        expected_report = {
            "allDurationInSeconds": 97.0,
            "MemoryCost": 4.0,
            "InvocationCost": 1.5,
            "totalCost": 5.5,
            "potentialSavings": 0.5,
            "timeoutInvocations": 3.0,
            "memoryExceededInvocation": 5.0,
            "avgCostPerInvocation": 0.5833333333,
            "avgMaxMemoryUsedMB": 101.3333333333,
            "avgOverProvisionedMB": 69.3333333333,
            "avgProvisionedMemoryMB": 170.6666666667,
            "avgDurationPerInvocation": 3.0,
            "reportID": report_id,
            "startDate": start_date,
            "endDate": end_date,
            "status": "Completed"
        }
        self.assertDictEqual(report, expected_report)
