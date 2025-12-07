.PHONY: build-frontend build-api run-api test-api stop-api logs clean help test deploy

# Docker image name
IMAGE_NAME := lambda-cost-analysis-api
CONTAINER_NAME := lambda-api-local
API_HANDLER := backend.api.app.lambda_handler
PORT := 9000

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build-frontend: ## Build the frontend
	cd frontend && npm run build

build-api: ## Build the Docker image for the API
	@echo "Building Docker image..."
	cd infrastructure && docker build -t $(IMAGE_NAME) .
	@echo "✅ Docker image built successfully"

run-api: ## Run the API locally on port 9000
	@echo "Starting Lambda API locally on http://localhost:$(PORT)..."
	@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):8080 \
		-e BUCKET_NAME=local-test-bucket \
		-e AWS_ACCESS_KEY_ID=test \
		-e AWS_SECRET_ACCESS_KEY=test \
		-e AWS_DEFAULT_REGION=us-east-1 \
		$(IMAGE_NAME) \
		$(API_HANDLER)
	@echo "✅ API running at http://localhost:$(PORT)/2015-03-31/functions/function/invocations"
	@echo ""
	@echo "Test endpoints:"
	@echo "  GET  /lambda-functions  - List Lambda functions"
	@echo "  GET  /report            - Get analysis report (requires reportID)"
	@echo "  GET  /reportSummaries   - List historical reports"
	@echo ""
	@echo "View logs: make logs"
	@echo "Stop API:  make stop-api"

logs: ## Show logs from the running API container
	docker logs -f $(CONTAINER_NAME)

stop-api: ## Stop the running API container
	@echo "Stopping API container..."
	@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	@echo "✅ API stopped"

test-api: ## Test the API endpoints
	@echo "Testing API endpoints..."
	@echo ""
	@echo "1. Testing /lambda-functions endpoint..."
	@curl -X POST http://localhost:$(PORT)/2015-03-31/functions/function/invocations \
		-H "Content-Type: application/json" \
		-d '{"path": "/lambda-functions", "httpMethod": "GET", "queryStringParameters": null}' \
		2>/dev/null | python3 -m json.tool || echo "❌ Failed to call /lambda-functions"
	@echo ""
	@echo "2. Testing /reportSummaries endpoint..."
	@curl -X POST http://localhost:$(PORT)/2015-03-31/functions/function/invocations \
		-H "Content-Type: application/json" \
		-d '{"path": "/reportSummaries", "httpMethod": "GET", "queryStringParameters": {}}' \
		2>/dev/null | python3 -m json.tool || echo "❌ Failed to call /reportSummaries"
	@echo ""
	@echo "✅ API tests complete"

test: ## Run Python tests
	uv run pytest src/tests -v

clean: stop-api ## Stop API and remove Docker image
	@echo "Removing Docker image..."
	@docker rmi $(IMAGE_NAME) 2>/dev/null || true
	@echo "✅ Cleanup complete"

deploy: build-frontend test ## Deploy to AWS
	cd infrastructure && AWS_PROFILE=shifted cdk deploy --all
