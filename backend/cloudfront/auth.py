import base64

def lambda_handler(event, context):
    # Get request and request headers
    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    # Configure authentication
    auth_user = 'test'
    auth_pass = 'admin123'

    # Construct the Basic Auth string
    auth_string = 'Basic ' + base64.b64encode(f'{auth_user}:{auth_pass}'.encode()).decode()

    # Require Basic authentication
    if 'authorization' not in headers or headers['authorization'][0]['value'] != auth_string:
        body = 'Unauthorized'
        response = {
            'status': '401',
            'statusDescription': 'Unauthorized',
            'body': body,
            'headers': {
                'www-authenticate': [{'key': 'WWW-Authenticate', 'value': 'Basic'}]
            }
        }
        return response

    # Continue request processing if authentication passed
    return request
