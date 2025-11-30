"""Aggregate Lambda cost analysis results from multiple CSV files."""

import json
import os
from datetime import datetime
from io import StringIO
from typing import Any

import pandas as pd
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from backend.utils.multithread_utils import multi_thread
from backend.utils.s3_utils import download_from_s3, upload_file_to_s3

logger = Logger()

bucket_name = os.environ["BUCKET_NAME"]


def download_csv_file_wrapper(s3_info: dict[str, str]) -> pd.DataFrame:
    """
    Download CSV file from S3 and parse as DataFrame.

    Parameters
    ----------
    s3_info : dict
        S3 file location with filename, bucket, and directory

    Returns
    -------
    DataFrame
        Parsed CSV data
    """
    csv_file_content = download_from_s3(
        file_name=s3_info["filename"],
        bucket_name=s3_info["bucket"],
        directory=s3_info["directory"],
    )
    return pd.read_csv(StringIO(csv_file_content), sep=",")


@logger.inject_lambda_context(log_event=True)  # type: ignore[misc]
def lambda_handler(event: list[dict[str, Any]], context: LambdaContext) -> None:
    """
    Aggregate cost analysis results and generate summary.

    Parameters
    ----------
    event : list of dict
        List of S3 file locations with analysis results
    context : LambdaContext
        Lambda context object
    """
    report_id = event[0]["report_id"]
    start_date = event[0]["start_date"]
    end_date = event[0]["end_date"]
    logger.info(
        "Aggregating data for report",
        extra={"report_id": report_id, "num_files": len(event)},
    )
    aggregated_data = pd.DataFrame()
    files_content = multi_thread(download_csv_file_wrapper, event, max_workers=10)
    for content in files_content:
        aggregated_data = pd.concat([aggregated_data, content], ignore_index=False)

    csv_buffer = StringIO()
    aggregated_data.to_csv(csv_buffer)
    upload_file_to_s3(
        csv_buffer.getvalue(),
        file_name="analysis.csv",
        bucket_name=bucket_name,
        directory=report_id,
    )
    avg_columns_rename = {
        "provisionedMemoryMB": "avgProvisionedMemoryMB",
        "maxMemoryUsedMB": "avgMaxMemoryUsedMB",
        "overProvisionedMB": "avgOverProvisionedMB",
    }

    aggregated_data.rename(columns=avg_columns_rename, inplace=True)
    agg_funcs = {
        "countInvocations": "sum",
        "allDurationInSeconds": "sum",
        "MemoryCost": "sum",
        "InvocationCost": "sum",
        "totalCost": "sum",
        "potentialSavings": "sum",
        "timeoutInvocations": "sum",
        "logSizeGB": "sum",
        "logIngestionCost": "sum",
        "logStorageCost": "sum",
        "analysisCost": "sum",
        "avgCostPerInvocation": "mean",
        "avgMaxMemoryUsedMB": "mean",
        "avgOverProvisionedMB": "mean",
        "avgProvisionedMemoryMB": "mean",
        "avgDurationPerInvocation": "mean",
    }
    # Apply the aggregation function
    result = aggregated_data.agg(agg_funcs)

    result["status"] = "Completed"
    result["reportID"] = report_id
    result["startDate"] = start_date
    result["endDate"] = end_date
    # Convert the result to JSON
    result_json = result.to_json()
    upload_file_to_s3(
        body=result_json,
        file_name="summary.json",
        bucket_name=bucket_name,
        directory=report_id,
    )
    upload_file_to_s3(
        body=result_json,
        file_name=f"{generate_reversed_timestamp()}_{report_id}.json",
        bucket_name=bucket_name,
        directory="summaries",
    )


def generate_reversed_timestamp() -> int:
    """
    Generate reversed timestamp for chronological sorting.

    Returns
    -------
    int
        Seconds until January 1, 2050
    """
    # Target future date (e.g., January 1, 2050)
    future_date = datetime(2050, 1, 1)

    # Current time in UTC
    now = datetime.now()

    # Calculate the difference in seconds
    delta = future_date - now

    reversed_timestamp = int(delta.total_seconds())
    return reversed_timestamp


if __name__ == "__main__":
    event = [
        {
            "filename": "c79a20af-c2d9-490f-90f3-c2046a34c8f5.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "783d4905-9f29-4342-9233-2a0a965b0764.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "2cf2c071-0045-4fbe-9461-bb8722267c03.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "fc038d19-f230-4dbf-8923-4cbc849bc8ad.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "d7271e18-6fe1-4a06-a5f5-844f8be3cca5.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "63697cbb-fda7-46e1-b82e-1b5a449ecdb2.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "414a1185-9d7a-4a9d-9eb9-aeea849da925.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "ea59058b-91cd-4c26-875a-f1d7b2705e5c.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "500b77cc-abe7-4ce0-9564-96f181a7762c.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "725b98db-3be2-483a-a3bc-5669ef5653c3.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "92f7234e-fe81-404a-9a23-ba225d8b1258.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "9b40025e-d108-4dac-aada-a9b7536ead99.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "ea7623d7-3aaf-42d1-95aa-af7de00909e5.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "580bd1a9-b932-402b-8f59-3f624cc8f24e.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "50408100-b99a-49bd-aebe-3fb7eb13318b.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "86b83d84-51e6-4604-8cb4-8776c907af69.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "55f73d38-b3d0-49dc-9710-7d1c9407e606.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "dd677f65-b30a-48b0-9446-d4bced78f152.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "7f9e7568-200b-4837-a6d2-16f640c28154.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "89429454-8fd3-4282-af61-c81f31d76068.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "16275ec7-03ca-4ca7-833b-84f876b04988.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "baaf80d2-a507-4d19-bb53-83862ec8f42c.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "6fb53064-fa60-498c-a305-72f71e9e32bb.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "59690ecb-4474-456b-8bb0-e4eb8b57e8c1.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "4c297112-3591-4388-9778-cb484a1e89dc.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "d5353053-8d1b-4aa6-addb-8fab564c4ec2.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "f5c46b44-cd25-4082-abe4-63888371d0f2.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "3cabd9b1-ffd7-4784-8545-1b45c746f543.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "85917dc0-bfb2-4655-ad0c-f8bfe063b9ee.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "3e46072d-bc9a-4829-b35b-8c1e165c7dd8.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "ed00e2a3-2b24-478c-b44f-4fc53bf27040.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "e8c1daf4-9fd8-4795-9949-6c67b3d3c6a6.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "7c85dbad-781b-4f6a-94ed-c209842aa388.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "d8c31089-bbdd-4f7b-9a3c-bce73f7f8908.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "e3af9631-24ad-4df3-9f08-3457722b0498.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "877ac4e1-b336-46a8-9753-e7a987b1c015.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "32e15fee-d4cd-4802-85d6-d935a8f786a6.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "3bcde5ef-fe18-489b-8072-d27e3c77365b.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "2a1b72bc-d314-41f9-825c-855bb402d4c7.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "cb83e744-f559-4c68-bccf-913939ef09c4.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "c0602edb-a036-42ac-90bd-073ced83bec5.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "28d60bf1-b4af-4b73-b160-f2613356ee65.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "4ca6a939-c9ac-4042-ac68-a0090419f9dd.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "7c35190b-f2cf-4b5a-8698-bb81bf57ce6d.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "b630dfe4-d96d-473d-aa34-e96a4bdac3ff.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "a664b87a-8d77-434b-9c5c-440cc903e970.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "ba455ba5-4750-4d26-ba59-21fc97f9a2a3.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "033c4a6b-85b5-40a4-8777-f17f9b64e7f0.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "8d9a50f0-e983-427f-abe7-81862dbd55d0.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "69f28148-5867-4c08-9616-6ee6834749c6.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "572312f9-1814-490a-90d1-82991a5cdd04.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "9ff355b9-5819-4254-974a-4c6163e18b45.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "1975281b-3053-4340-ae0f-aa980d101c77.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "f57a6c2a-544a-4577-94ec-328f67261c6d.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "7461749a-a288-4328-baf2-a02dad6ce95d.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "c836cd3f-21b2-49f8-99a1-ba3883c5eb3a.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "68982983-adbc-42ba-844d-80efa0816f49.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "987ca22a-22bd-4b76-a57c-43b5afc907ac.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "e43ce79e-eedb-4ffe-ab0d-9f076dd461d4.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "a9016b89-a8cf-4700-88b5-a71087430a87.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "c8fbdc00-7acf-4c88-ac11-5bdfa423493d.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "9e742d48-c7a7-4a30-a969-327b91932371.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "3f708040-eb11-45a8-a602-a7a81df7d315.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "5db8b3ff-9513-4a08-9b61-d3f99f6af9f9.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "1a35e6c2-d09c-4ced-b2b7-6be0fa050cdf.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "78471bfe-8983-4206-b0e3-adf9ded2c8d5.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "d33d9baf-67b9-429f-901e-f570ef8842c1.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "d7b40fc3-9407-41e3-8845-6aabe9318da4.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "82594f41-e0f3-4ac7-9b44-95eeb8610c4b.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "e2c67b48-e038-4105-8a0e-5066488edeab.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "963c4eeb-10c1-4938-b22b-0ef0ddb07bef.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "eb7d9188-cbd1-40b0-9b1e-a4a811b411f1.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "c33640e0-55f5-4e4b-b103-52ef81511abf.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "eaf78d17-30a4-4c06-ad44-71093f19e34b.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "a7406494-b4f7-42ea-acd2-55e143d1bfeb.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "da1fde4b-efa5-4613-aa1c-2a96004e75f1.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "46387bd3-3c77-4489-ba7d-a4a03d12bf55.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "4176b1fa-01e9-4a46-af29-6506a5b7d350.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "64b08c8f-e4e3-4c9f-a482-9bc912a05b68.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "25324f5a-5b4e-4820-b0d5-36deac517b03.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "aea170f5-7ba3-4b85-bfcb-11f20412ba39.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "ba495f76-cd8a-4606-9101-059cda8a3a97.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
        {
            "filename": "5e167db2-b2f2-477d-a968-a436bd81c8f8.csv",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "single_analysis/1720711632",
            "report_id": 1720711632,
            "start_date": "2024-05-31T23:00:00.000Z",
            "end_date": "2024-06-30T22:59:59.999Z",
        },
    ]
    lambda_handler(event, None)
