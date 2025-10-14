import base64

import boto3

# Explicitly specify us-east-1 for SSM client as Parameters are created in that region.
ssm = boto3.client("ssm", region_name="us-east-1")


def get_ssm_parameter(name):
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response["Parameter"]["Value"]


# Configure authentication
auth_user = get_ssm_parameter("/lambda-cost-analysis/username")
auth_pass = get_ssm_parameter("/lambda-cost-analysis/password")


def lambda_handler(event, context):
    # Get request and request headers
    request = event["Records"][0]["cf"]["request"]
    headers = request["headers"]

    # Construct the Basic Auth string
    auth_string = (
        "Basic " + base64.b64encode(f"{auth_user}:{auth_pass}".encode()).decode()
    )

    # Require Basic authentication
    if (
        "authorization" not in headers
        or headers["authorization"][0]["value"] != auth_string
    ):
        body = "Unauthorized"
        response = {
            "status": "401",
            "statusDescription": "Unauthorized",
            "body": body,
            "headers": {
                "www-authenticate": [{"key": "WWW-Authenticate", "value": "Basic"}]
            },
        }
        return response

    # Continue request processing if authentication passed
    return request
