"""Shared pytest fixtures for all tests."""

from dataclasses import dataclass

import pytest


@dataclass
class LambdaContext:
    """Mock AWS Lambda context for testing."""

    function_name: str = "test-function"
    function_version: str = "$LATEST"
    invoked_function_arn: str = (
        "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    )
    memory_limit_in_mb: int = 128
    aws_request_id: str = "test-request-id"
    log_group_name: str = "/aws/lambda/test-function"
    log_stream_name: str = "2024/01/01/[$LATEST]test-stream"

    def get_remaining_time_in_millis(self) -> int:
        """Return mock remaining time."""
        return 300000


@pytest.fixture
def lambda_context() -> LambdaContext:
    """Provide a mock Lambda context for tests."""
    return LambdaContext()
