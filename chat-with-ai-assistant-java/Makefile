.PHONY: setup run test docker-build docker-run

setup:
	mvn install -DskipTests

run:
	mvn spring-boot:run

test:
	mvn compile

docker-build:
	docker build -t $$(basename $$(pwd)) .

docker-run:
	docker run --env-file .env -p 8080:8080 $$(basename $$(pwd))
