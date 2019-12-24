NAME=ngs360-flaskapp
.PHONY: build test run clean

clean:
	rm -rf config.pyc .coverage .pytest_cache/ __pycache__/ htmlcov/ .venv/ .env

build: clean
	docker build -t $(NAME) .

env: requirements.txt requirements-dev.txt
	python3 -m venv .venv
	source .venv/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt

test: env
	source .venv/bin/activate && python -m pytest -v --cov app/ && coverage html && PYTHONPATH="." pylint app tests --load-plugins pylintplugins

run: env
	echo "FLASK_ENV=development" > .env
	source .venv/bin/activate && python application.py
