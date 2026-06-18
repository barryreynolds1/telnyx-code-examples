.PHONY: setup run docker-build docker-run

setup:
	pip install -r requirements.txt

run:
	python app.py

docker-build:
	docker build -t texml-dynamic-call-router-python .

docker-run:
	docker run --env-file .env -p 5000:5000 texml-dynamic-call-router-python
