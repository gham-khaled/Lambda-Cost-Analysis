# Multi-stage build for AWS Lambda Python functions
FROM public.ecr.aws/lambda/python:3.10 AS builder

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml /build/
COPY src/ /build/src/

# Install dependencies to /build/deps
WORKDIR /build
RUN uv pip install --python 3.10 --no-cache --target /build/deps .

# Final stage
FROM public.ecr.aws/lambda/python:3.10

# Copy installed dependencies
COPY --from=builder /build/deps/ ${LAMBDA_TASK_ROOT}/

# Copy application code
COPY src/backend/ ${LAMBDA_TASK_ROOT}/backend/

# Lambda handler will be set via CMD in CDK construct
