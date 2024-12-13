build_frontend:
	cd frontend && npm run build
test:
	cd backend && python3 -m unittest
deploy: build_frontend  test
	cd infrastructure && cdk deploy --all --profile sinda