.PHONY: setup run test docker-build docker-run

setup:
	npm install

run:
	node server.js

test:
	node --check server.js

docker-build:
	docker build -t run-llm-inference-nodejs .

docker-run:
	docker run --env-file .env -p 5000:5000 run-llm-inference-nodejs
