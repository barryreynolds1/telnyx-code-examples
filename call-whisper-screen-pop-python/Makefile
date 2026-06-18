.PHONY: setup run docker-build docker-run

setup:
	pip install -r requirements.txt

run:
	python app.py

docker-build:
	docker build -t call-whisper-screen-pop-python .

docker-run:
	docker run --env-file .env -p 5000:5000 call-whisper-screen-pop-python
