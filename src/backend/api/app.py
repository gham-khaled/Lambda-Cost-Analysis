"""Shared API Gateway resolver for Lambda Cost Analysis API.

This module provides the shared APIGatewayRestResolver instance that
route modules import and register their endpoints with.
"""

from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()

# Shared CORS configuration
cors_config = CORSConfig(allow_origin="*", max_age=300)

# Shared API Gateway resolver - routes will register with this instance
app = APIGatewayRestResolver(cors=cors_config)


# Import routes to register them with the app
# These imports must come after app is defined so routes can import it
from backend.api import get_analysis_report  # noqa: E402, F401
from backend.api import historical_analysis_report  # noqa: E402, F401
from backend.api import list_lambda_functions  # noqa: E402, F401


@logger.inject_lambda_context(log_event=True)  # type: ignore[misc]
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Lambda handler with Powertools event resolver."""
    return app.resolve(event, context)  # type: ignore[no-any-return]
