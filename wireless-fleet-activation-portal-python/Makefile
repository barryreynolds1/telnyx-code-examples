.PHONY: setup run docker-build docker-run

setup:
	pip install -r requirements.txt

run:
	python app.py

docker-build:
	docker build -t wireless-fleet-activation-portal-python .

docker-run:
	docker run --env-file .env -p 5000:5000 wireless-fleet-activation-portal-python
