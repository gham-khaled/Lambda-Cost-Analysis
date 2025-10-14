"""CORS headers decorator for Lambda functions."""

from typing import Any, Callable

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "OPTIONS,GET,PUT,POST,DELETE",
}


def cors_header(func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    """
    Add CORS headers to Lambda response.

    Parameters
    ----------
    func : Callable
        Lambda handler function.

    Returns
    -------
    Callable
        Decorated function with CORS headers.
    """

    def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        response = func(*args, **kwargs)

        if isinstance(response, dict):
            response["headers"] = CORS_HEADERS
        return response

    return wrapper
