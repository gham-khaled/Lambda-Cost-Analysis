import json
import logging
import os
from utils.sf_utils import upload_divided_params
from utils.s3_utils import upload_file_to_s3

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bucket_name = os.environ['BUCKET_NAME']
max_arn_per_invocation = 5
def lambda_handler(event, context):
    lambda_functions_name = event['lambda_functions_name']

    report_id = event['report_id']
    start_date = event.get('start_date')
    end_date = event.get('end_date')
    upload_file_to_s3(body=json.dumps({'status': 'Running'}),
                      file_name='summary.json',
                      bucket_name=bucket_name,
                      directory=report_id)
    sf_parameters = upload_divided_params(lambda_functions_name, divider=max_arn_per_invocation,
                                          bucket_name=bucket_name,
                                          directory_name='SF_PARAMS/SF_PARAMS')
    return {
        'lambda_functions_name': sf_parameters,
        'start_date': start_date,
        'end_date': end_date,
        'report_id': report_id
    }


if __name__ == '__main__':
    test = "{\"allDurationInSeconds\":101.689,\"avgProvisionedMemoryMB\":122.0703,\"MemoryCost\":0.000202,\"InvocationCost\":0.0000088,\"totalCost\":0.0002108,\"avgCostPerInvocation\":0.000004792,\"avgMaxMemoryUsedMB\":80.1086,\"avgOverProvisionedMB\":41.9617,\"optimalTotalCost\":0.0002119,\"potentialSavings\":0.0,\"avgDurationPerInvocation\":2.3111,\"status\":\"Completed\"}"

    logger.info(json.dumps(json.loads(test), indent=4))
