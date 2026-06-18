.PHONY: setup run test clean
setup:
	pip install -r requirements.txt
run:
	python app.py
test:
	python -m py_compile app.py && echo "Syntax OK"
clean:
	find . -name __pycache__ -exec rm -rf {} +
