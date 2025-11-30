import csv
import json
import os
from io import StringIO

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
        s3 = boto3.resource("s3", region_name="us-east-1")
        bucket = s3.Bucket(bucket_name)
        bucket.create()
        os.environ["BUCKET_NAME"] = bucket_name
        yield bucket_name


def write_csv_file(csv_dict_content):
    """Helper function to write CSV data to a StringIO buffer."""
    csv_buffer = StringIO()
    field_names = csv_dict_content[0].keys()

    writer = csv.DictWriter(csv_buffer, fieldnames=field_names, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(csv_dict_content)
    return csv_buffer


@mock_aws
def test_file_merge(s3_bucket, lambda_context):
    """Testing that the CSV files are merged correctly."""
    from backend.step_function.analysis_aggregator import lambda_handler
    from backend.utils.s3_utils import download_from_s3, upload_file_to_s3

    report_id = "test-report"
    start_date = "X"
    end_date = "X"
    directory = f"single_analysis/{report_id}"

    file1 = [
        {
            "functionName": "LambdaA",
            "runtime": "python3.10",
            "countInvocations": 10,
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
            "logSizeGB": 0.001,
            "logIngestionCost": 0.0005,
            "logStorageCost": 0.00003,
            "analysisCost": 0.000005,
            "timeoutInvocations": 0,
        }
    ]
    file2 = [
        {
            "functionName": "LambdaC",
            "runtime": "python3.10",
            "countInvocations": 15,
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
            "logSizeGB": 0.001,
            "logIngestionCost": 0.0005,
            "logStorageCost": 0.00003,
            "analysisCost": 0.000005,
            "timeoutInvocations": 0,
        }
    ]

    upload_file_to_s3(
        body=write_csv_file(file1).getvalue(),
        bucket_name=s3_bucket,
        file_name="file1.csv",
        directory=directory,
    )
    upload_file_to_s3(
        body=write_csv_file(file2).getvalue(),
        bucket_name=s3_bucket,
        file_name="file2.csv",
        directory=directory,
    )

    event = [
        {
            "filename": "file1.csv",
            "bucket": s3_bucket,
            "directory": directory,
            "report_id": report_id,
            "start_date": start_date,
            "end_date": end_date,
        },
        {
            "filename": "file2.csv",
            "bucket": s3_bucket,
            "directory": directory,
            "report_id": report_id,
            "start_date": start_date,
            "end_date": end_date,
        },
    ]
    lambda_handler(event, lambda_context)
    csv_body = download_from_s3("analysis.csv", s3_bucket, report_id)
    csv_file = StringIO(csv_body)

    # Use the csv.DictReader to read the CSV file and convert it to a list of dictionaries
    reader = csv.DictReader(csv_file)
    data_list = [dict(row) for row in reader]
    for data in data_list:
        del data[""]
    files_merge = file1 + file2
    for file in files_merge:
        for key, value in list(file.items()):
            file[key] = str(value)

    files_merge = sorted(files_merge, key=lambda x: x["functionName"])
    data_list = sorted(data_list, key=lambda x: x["functionName"])

    assert len(data_list) == 2
    assert data_list == files_merge


@mock_aws
def test_summary_file(s3_bucket, lambda_context):
    """Testing that the summary file is created correctly."""
    from backend.step_function.analysis_aggregator import lambda_handler
    from backend.utils.s3_utils import download_from_s3, upload_file_to_s3

    report_id = "test-report"
    directory = f"single_analysis/{report_id}"
    start_date = "X"
    end_date = "X"
    file1 = [
        {
            "functionName": "LambdaA",
            "runtime": "python3.10",
            "countInvocations": 10,
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
            "logSizeGB": 0.002,
            "logIngestionCost": 0.001,
            "logStorageCost": 0.00006,
            "analysisCost": 0.00001,
            "timeoutInvocations": 2,
        },
        {
            "functionName": "LambdaB",
            "runtime": "python3.10",
            "countInvocations": 20,
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
            "logSizeGB": 0.003,
            "logIngestionCost": 0.0015,
            "logStorageCost": 0.00009,
            "analysisCost": 0.000015,
            "timeoutInvocations": 1,
        },
    ]
    file2 = [
        {
            "functionName": "LambdaC",
            "runtime": "python3.10",
            "countInvocations": 15,
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
            "logSizeGB": 0.001,
            "logIngestionCost": 0.0005,
            "logStorageCost": 0.00003,
            "analysisCost": 0.000005,
            "timeoutInvocations": 0,
        }
    ]

    upload_file_to_s3(
        body=write_csv_file(file1).getvalue(),
        bucket_name=s3_bucket,
        file_name="file1.csv",
        directory=directory,
    )
    upload_file_to_s3(
        body=write_csv_file(file2).getvalue(),
        bucket_name=s3_bucket,
        file_name="file2.csv",
        directory=directory,
    )

    event = [
        {
            "filename": "file1.csv",
            "bucket": s3_bucket,
            "directory": directory,
            "report_id": report_id,
            "start_date": start_date,
            "end_date": end_date,
        },
        {
            "filename": "file2.csv",
            "bucket": s3_bucket,
            "directory": directory,
            "report_id": report_id,
            "start_date": start_date,
            "end_date": end_date,
        },
    ]
    lambda_handler(event, lambda_context)
    report = json.loads(
        download_from_s3("summary.json", bucket_name=s3_bucket, directory=report_id)
    )

    expected_report = {
        "countInvocations": 45.0,
        "allDurationInSeconds": 97.0,
        "MemoryCost": 4.0,
        "InvocationCost": 1.5,
        "totalCost": 5.5,
        "potentialSavings": 0.5,
        "timeoutInvocations": 3.0,
        "logSizeGB": 0.006,
        "logIngestionCost": 0.003,
        "logStorageCost": 0.00018,
        "analysisCost": 0.00003,
        "avgCostPerInvocation": 0.5833333333,
        "avgMaxMemoryUsedMB": 101.3333333333,
        "avgOverProvisionedMB": 69.3333333333,
        "avgProvisionedMemoryMB": 170.6666666667,
        "avgDurationPerInvocation": 3.0,
        "reportID": report_id,
        "startDate": start_date,
        "endDate": end_date,
        "status": "Completed",
    }
    assert report == expected_report
