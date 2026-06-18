.PHONY: setup run test docker-build docker-run

setup:
	npm install

run:
	node server.js

test:
	node --check server.js

docker-build:
	docker build -t $$(basename $$(pwd)) .

docker-run:
	docker run --env-file .env -p 5000:5000 $$(basename $$(pwd))
