# Multi-stage build for AWS Lambda Python functions
FROM public.ecr.aws/lambda/python:3.13 AS builder

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml /build/
COPY src/ /build/src/

# Install dependencies to /build/deps
WORKDIR /build
RUN uv pip install --python 3.13 --no-cache --target /build/deps .

# Final stage
FROM public.ecr.aws/lambda/python:3.13

# Copy installed dependencies and application code
COPY --from=builder /build/deps/ ${LAMBDA_TASK_ROOT}/

# Set the Lambda handler
# This will be overridden by CDK for different Lambda functions
CMD ["backend.api.app.lambda_handler"]
