import json
import os
import unittest
import boto3
from datetime import datetime, timedelta
import time

# Import the function to be tested
import moto
from moto import mock_aws


@mock_aws
class TestAnalysisGenerator(unittest.TestCase):
    def setUp(self):
        self.mock_aws = moto.mock_aws()
        self.mock_aws.start()
        os.environ['BUCKET_NAME'] = ""
        self.logs = boto3.client("logs")

    def tearDown(self):
        self.mock_aws.stop()

    def test_get_lambda_cost(self):
        log_group_name = "/aws/lambda/test_lambda"
        log_stream_name = "logStream"

        # Create log group and log stream
        self.logs.create_log_group(logGroupName=log_group_name)
        self.logs.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)

        # Add sample log events
        log_events = [
            {
                'timestamp': int((datetime.utcnow() - timedelta(minutes=3)).timestamp() * 1000),
                'message': "Task timed out after 10.00 seconds"
            },
            {
                'timestamp': int((datetime.utcnow() - timedelta(minutes=2)).timestamp() * 1000),
                'message': "Error: Runtime exited with error"
            },
            {
                'timestamp': int((datetime.utcnow() - timedelta(minutes=1)).timestamp() * 1000),
                'message': "REPORT RequestId: 123456789 Duration: 1000 ms Billed Duration: 1000 ms Memory Size: 128 MB Max Memory Used: 70 MB"
            }

        ]

        self.logs.put_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            logEvents=log_events
        )

        # Call the function
        # from step_function.analysis_generator import get_lambda_cost
        # result = get_lambda_cost("test_lambda", "python3.8", days=7, cpu_type='x86_64')
        # print(result)
        # Assert the expected result
        # expected_result = {
        #     "functionName": "test_lambda",
        #     "runtime": "python3.8",
        #     "timeoutInvocations": "1",
        #     "countInvocations": "1",
        #     "memoryExceededInvocation": "1",
        #     "singleInvocationCost": "0.0000002",
        #     "GBSecondPrice": "0.0000166667",
        #     "allDurationInSeconds": "1.0",
        #     "provisionedMemoryMB": "128",
        #     "GbSecondsConsumed": "0.125",
        #     "MemoryCost": "0.0000020833",
        #     "InvocationCost": "0.0002",
        #     "totalCost": "0.0002020833",
        #     "avgCostPerInvocation": "0.0002020833",
        #     "maxMemoryUsedMB": "70",
        #     "overProvisionedMB": "58",
        #     "optimalMemory": "84.0",
        #     "optimalTotalCost": "0.0002020833",
        #     "potentialSavings": "0",
        #     "avgDurationPerInvocation": "1.0"
        # }

        # for key, value in expected_result.items():
        #     self.assertAlmostEqual(float(result[key]), float(value), places=6)


if __name__ == '__main__':
    unittest.main()

