import boto3
import json
import logging

from api.cors_decorator import cors_header

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = boto3.client('lambda')


def fetch_lambda_function(marker=None):
    response = client.list_functions(Marker=marker) if marker else client.list_functions()
    functions = []
    for function in response['Functions']:
        functions.append({
            'FunctionName': function['FunctionName'],
            'Runtime': function.get('Runtime', "Docker Image"),
            'PackageType': function['PackageType'],
            'Architectures': function['Architectures'],
            'MemorySize': function['MemorySize'],
            'LastModified': function['LastModified']
        })

    if 'NextMarker' in response:
        return functions + fetch_lambda_function(response['NextMarker'])

    return functions


lambda_functions = fetch_lambda_function()


# TODO: Add more information in the response body
@cors_header
def lambda_handler(event, context):
    #     parameters = event['queryStringParameters']
    #     selected_runtimes = parameters['selectedRuntime']
    #     selected_package_type = parameters['selectedPackageType']
    #     selected_architecture = parameters['selectedArchitecture']

    return {
        'statusCode': 200,
        'body': json.dumps(lambda_functions),
    }


if __name__ == '__main__':
    logger.info(lambda_handler(None, None))
