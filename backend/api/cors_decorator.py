CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE'
}


def cors_header(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        if isinstance(response, dict):
            response["headers"] = CORS_HEADERS
        return response

    return wrapper
