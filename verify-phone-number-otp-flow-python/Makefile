.PHONY: setup run docker-build docker-run

setup:
	pip install -r requirements.txt

run:
	python app.py

docker-build:
	docker build -t verify-phone-number-otp-flow-python .

docker-run:
	docker run --env-file .env -p 5000:5000 verify-phone-number-otp-flow-python
