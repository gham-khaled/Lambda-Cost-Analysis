"""Generate Lambda cost analysis from CloudWatch Logs Insights."""

import concurrent.futures
import csv
import os
import time
import uuid
from datetime import datetime
from io import StringIO
from typing import Any

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.config import Config
from botocore.exceptions import ClientError

from backend.utils.s3_utils import upload_file_to_s3
from backend.utils.sf_utils import download_parameters_from_s3

logger = Logger()

# Configure boto3 client with retry strategy for CloudWatch Logs
retry_config = Config(
    retries={
        "max_attempts": 10,
        "mode": "adaptive",  # Uses exponential backoff with adaptive retry strategy
    }
)

lambda_client = boto3.client("lambda")
bucket_name = os.environ["BUCKET_NAME"]


@logger.inject_lambda_context(log_event=True)  # type: ignore[misc]
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """
    Generate cost analysis for a batch of Lambda functions.

    Parameters
    ----------
    event : dict
        Event with lambda_functions_name S3 location, report_id, start_date, end_date
    context : LambdaContext
        Lambda context object

    Returns
    -------
    dict
        S3 location of generated CSV analysis file
    """
    lambda_functions_name = download_parameters_from_s3(event["lambda_functions_name"])
    report_id = event.get("report_id", "")
    start_date = event.get("start_date", "")
    end_date = event.get("end_date", "")
    logger.info(
        "Processing lambda functions",
        extra={"num_functions": len(lambda_functions_name), "report_id": report_id},
    )
    return generate_cost_report(lambda_functions_name, report_id, start_date, end_date)


def get_lambda_cost(
    lambda_name: str, start_date: str, end_date: str
) -> dict[str, Any] | None:
    """
    Calculate cost metrics for a Lambda function.

    Parameters
    ----------
    lambda_name : str
        Lambda function name
    start_date : str
        Analysis start date (ISO format)
    end_date : str
        Analysis end date (ISO format)

    Returns
    -------
    dict or None
        Cost analysis metrics or None if log group doesn't exist
    """
    start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    response = lambda_client.get_function_configuration(FunctionName=lambda_name)

    runtime, memory_size, architecture = (
        response.get("Runtime", "Docker Image"),
        response["MemorySize"],
        response["Architectures"][0],
    )
    storage_size, log_group_name = (
        response["EphemeralStorage"]["Size"],
        response["LoggingConfig"]["LogGroup"],
    )
    if not check_log_group_exist(log_group_name):
        return None
    query_response = run_cloudwatch_query(
        log_group_name,
        start_datetime,
        end_datetime,
        memory_size,
        storage_size,
        architecture,
    )
    if not query_response:
        return None

    results = query_response[0]
    logger.info(f"Query results for {lambda_name}: {results}")

    answer = {
        "functionName": lambda_name,
        "runtime": runtime,
        "architecture": architecture,
    }
    for result in results:
        field, value = result["field"], result["value"]
        answer[field] = value
    if float(answer["potentialSavings"]) < 0:
        answer["potentialSavings"] = 0
        answer["optimalMemory"] = answer["provisionedMemoryMB"]
    return answer


def run_cloudwatch_query(
    log_group_name: str,
    start_datetime: datetime,
    end_datetime: datetime,
    memory_size: int,
    storage_size: int,
    architecture: str,
) -> list[list[dict[str, str]]] | None:
    """
    Execute CloudWatch Logs Insights query for cost analysis.

    Parameters
    ----------
    log_group_name : str
        CloudWatch log group name
    start_datetime : datetime
        Query start time
    end_datetime : datetime
        Query end time
    memory_size : int
        Lambda memory size in MB
    storage_size : int
        Lambda ephemeral storage size in MB
    architecture : str
        Lambda architecture (arm64 or x86_64)

    Returns
    -------
    list or None
        Query results or None on error
    """
    gb_second_memory_price = (
        "0.0000133334" if architecture == "arm64" else "0.0000166667"
    )
    gb_second_storage_price = "0.0000000309"
    query = f"""
    fields @timestamp, @message
    | parse @message "Process exited before completing request" as memory_exceeded_1
    | parse @message "[ERROR] MemoryError" as memory_exceeded_2
    | parse @message "Task timed out after *" as timeout_number_1
    | parse @message "Status: timeout" as timeout_number_2
    | parse @message "REPORT RequestId: *" as REPORT
    | stats  greatest(count(timeout_number_1) , 0) + greatest(count(timeout_number_2) , 0) as timeoutInvocations,
    count(REPORT) as countInvocations,
    greatest(count(memory_exceeded_1) , 0) + greatest(count(memory_exceeded_2) , 0) as memoryExceededInvocation,
    0.20 / 1000000 as singleInvocationCost,
    {gb_second_memory_price} as GBSecondMemoryPrice,
    {gb_second_storage_price} as GBSecondStoragePrice,
    {storage_size - 512} as StorageSizeMB,

    max(@memorySize / 1000000 ) as provisionedMemoryMB,
    sum(@billedDuration) / 1000 as allDurationInSeconds,
    allDurationInSeconds * provisionedMemoryMB / 1024 as GbSecondsMemoryConsumed,
    allDurationInSeconds * StorageSizeMB / 1024 as GbSecondsStorageConsumed,

    GbSecondsMemoryConsumed *  GBSecondMemoryPrice as MemoryCost,
    GbSecondsStorageConsumed *  GBSecondStoragePrice as StorageCost,
    countInvocations * singleInvocationCost as InvocationCost,

    MemoryCost + InvocationCost +  StorageCost as totalCost,

    max(@maxMemoryUsed  / 1000000 ) as maxMemoryUsedMB,
    greatest(provisionedMemoryMB - maxMemoryUsedMB, 0) as overProvisionedMB,
    greatest(maxMemoryUsedMB * 1.2, 128) as optimalMinMemory,
    least(optimalMinMemory, provisionedMemoryMB) as optimalMemory,

    allDurationInSeconds * optimalMemory * GBSecondMemoryPrice / 1024 as optimalMemoryCost,
    greatest(MemoryCost - optimalMemoryCost, 0) as potentialSavings,

    totalCost / countInvocations as avgCostPerInvocation,
    allDurationInSeconds / countInvocations as avgDurationPerInvocation
 """
    # Create CloudWatch client with retry configuration
    cloudwatch_client = boto3.client("logs", config=retry_config)

    try:
        query_id = cloudwatch_client.start_query(
            logGroupName=log_group_name,
            startTime=int(start_datetime.timestamp()),
            endTime=int(end_datetime.timestamp()),
            queryString=query,
        )["queryId"]

        # Poll for query completion with exponential backoff
        max_attempts = 30
        base_wait_time = 1
        attempt = 0

        while attempt < max_attempts:
            try:
                response = cloudwatch_client.get_query_results(queryId=query_id)

                if response["status"] == "Complete":
                    logger.debug(f"Query completed for {log_group_name}")
                    break
                elif response["status"] in ["Failed", "Cancelled", "Timeout"]:
                    logger.error(
                        f"Query {response['status'].lower()} for {log_group_name}"
                    )
                    return None

                # Exponential backoff: wait longer between each poll
                wait_time = min(base_wait_time * (2**attempt), 30)
                logger.debug(
                    f"Query status for {log_group_name}: {response['status']}, "
                    f"waiting {wait_time}s before retry"
                )
                time.sleep(wait_time)
                attempt += 1

            except ClientError as e:
                if e.response["Error"]["Code"] == "ThrottlingException":
                    # Additional backoff for throttling
                    wait_time = min(base_wait_time * (2 ** (attempt + 2)), 60)
                    logger.warning(
                        f"Throttled while polling query for {log_group_name}, "
                        f"waiting {wait_time}s before retry"
                    )
                    time.sleep(wait_time)
                    attempt += 1
                else:
                    raise

        if attempt >= max_attempts:
            logger.error(
                f"Query timed out after {max_attempts} attempts for {log_group_name}"
            )
            return None

        logger.debug(f"Query response for {log_group_name}: {str(response)[:20]}")

    except cloudwatch_client.exceptions.MalformedQueryException as e:
        logger.error(f"Malformed query for {log_group_name}: {e}")
        return None
    except ClientError as e:
        logger.error(f"AWS error while querying {log_group_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while querying {log_group_name}: {e}")
        return None

    return response["results"]  # type: ignore[no-any-return]


def check_log_group_exist(log_group_name: str) -> bool:
    """
    Check if CloudWatch log group exists.

    Parameters
    ----------
    log_group_name : str
        Log group name to check

    Returns
    -------
    bool
        True if log group exists
    """
    cloudwatch_client = boto3.client("logs", config=retry_config)

    try:
        log_groups = cloudwatch_client.describe_log_groups(
            logGroupNamePrefix=log_group_name
        )
        for log_group in log_groups["logGroups"]:
            if log_group["logGroupName"] == log_group_name:
                return True
        return False
    except ClientError as e:
        logger.error(f"Error checking if log group exists for {log_group_name}: {e}")
        return False


def generate_cost_report(
    lambda_list: list[str], report_id: Any, start_date: str, end_date: str
) -> dict[str, Any]:
    """
    Generate cost report CSV for multiple Lambda functions.

    Parameters
    ----------
    lambda_list : list of str
        Lambda function names to analyze
    report_id : Any
        Report identifier
    start_date : str
        Analysis start date
    end_date : str
        Analysis end date

    Returns
    -------
    dict
        S3 location of generated CSV file
    """
    lambda_costs = []
    logger.info(f"Processing lambda functions: {lambda_list}")
    # Reduced from 5 to 2 workers to avoid CloudWatch Logs API rate limits
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(get_lambda_cost, lambda_name, start_date, end_date)
            for lambda_name in lambda_list
        ]
        for future in concurrent.futures.as_completed(futures):
            lambda_costs.append(future.result())
    lambda_costs = [item for item in lambda_costs if item is not None]
    logger.debug(f"Lambda costs: {lambda_costs}")
    csv_buffer = StringIO()

    fieldnames = [
        "functionName",
        "runtime",
        "architecture",
        "allDurationInSeconds",
        "provisionedMemoryMB",
        "MemoryCost",
        "InvocationCost",
        "StorageCost",
        "totalCost",
        "avgCostPerInvocation",
        "maxMemoryUsedMB",
        "overProvisionedMB",
        "optimalMemory",
        "potentialSavings",
        "avgDurationPerInvocation",
        "timeoutInvocations",
        "memoryExceededInvocation",
    ]
    # with open(output_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for cost_data in lambda_costs:
        if cost_data is not None:
            writer.writerow(cost_data)
    filename = f"{str(uuid.uuid4())}.csv"
    directory = f"single_analysis/{report_id}"
    upload_file_to_s3(
        body=csv_buffer.getvalue(),
        bucket_name=bucket_name,
        file_name=filename,
        directory=directory,
    )
    logger.info(
        f"Lambda functions {lambda_list} for Report {report_id} have been uploaded to {filename}"
    )
    return {
        "filename": filename,
        "bucket": bucket_name,
        "directory": directory,
        "report_id": report_id,
        "start_date": start_date,
        "end_date": end_date,
    }


if __name__ == "__main__":
    # lambda_list = json.load(open('functions_details.json', 'r'))
    # lambda_functions_list = lambda_list['Functions']
    # generate_cost_report(lambda_functions_list[:10])
    event = {
        "end_date": "2024-06-30T22:59:59.999Z",
        "lambda_functions_name": {
            "filename": "params22.json",
            "bucket": "stepfunctionanalysisstack-analysisbucketd8638f5f-kcqlcippvvcs",
            "directory": "SF_PARAMS/SF_PARAMS2024-07-11-16:00:46",
        },
        "report_id": 1720713644,
        "start_date": "2024-05-31T23:00:00.000Z",
    }
    lambda_handler(event, None)
    # lambda_name = "shifted-dispatch-CheckForDeviceTOUDispatch-HKRtUoMwUI07"
    # lambda_name = "apricity-app-ConvertDataExportFunction-IUZJ3LLJ36AY"
    # start_date = "2024-05-31T23:00:00.000Z"
    # end_date = "2024-06-30T22:59:59.999Z"
    #
    # print(json.dumps(get_lambda_cost(lambda_name, start_date=start_date, end_date=end_date), indent=2))

    # arn_lambda_lists = ["serverless-ml-GroupForecastFunction-hmXiCccBJGiP",
    #                     "telemetry-daily-Insights-W-EfficiencyScoreFunction-7s1uoiVbOCyG",
    #                     "wattwatchers_get_telemetry",
    #                     "telemetry-daily-InsightStreamFunction-4PcyCebTyDBg",
    #                     "shifted-dispatch-CheckForDeviceTOUDispatch-HKRtUoMwUI07"]
    # generate_cost_report(arn_lambda_lists)
