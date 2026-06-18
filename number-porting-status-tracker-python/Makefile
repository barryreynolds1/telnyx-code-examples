.PHONY: setup run docker-build docker-run

setup:
	pip install -r requirements.txt

run:
	python app.py

docker-build:
	docker build -t number-porting-status-tracker-python .

docker-run:
	docker run --env-file .env -p 5000:5000 number-porting-status-tracker-python
