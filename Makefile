.PHONY: clean install build test lint browsertests run shell

all: clean install test lint build

clean:
	find . -name __pycache__ -exec rm -rf {} \;
	rm -rf *.pyc .coverage .pytest_cache/ htmlcov/ .venv/ .env

install: requirements.txt requirements-dev.txt
	python3 -m venv .venv
	source .venv/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt

build:
	docker build -t $(NAME) .

test:
	rm -rf .coverage htmlcov/
	source .venv/bin/activate && python -m pytest -vv --cov app/ --ignore=tests/FrontEnd && coverage html

lint:
	source .venv/bin/activate && PYTHONPATH="." pylint app tests --load-plugins pylintplugins --exit-zero

browsertests:
	source .venv/bin/activate && python3 -m pytest -v tests/FrontEnd

run:
	source .venv/bin/activate && python application.py

shell:
	source .venv/bin/activate && flask shell
