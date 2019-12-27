.PHONY: build test run clean shell

clean:
	rm -rf config.pyc .coverage .pytest_cache/ __pycache__/ htmlcov/ .venv/ .env

build: clean
	docker build -t $(NAME) .

env: requirements.txt requirements-dev.txt
	python3 -m venv .venv
	source .venv/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt

test: env
	rm -rf .coverage htmlcov/ .env
	source .venv/bin/activate && python -m pytest -vv --cov app/ && coverage html && PYTHONPATH="." pylint app tests --load-plugins pylintplugins --exit-zero

run: env
	cp development.env .env
	source .venv/bin/activate && python application.py
	rm .env

shell: env
	cp development.env .env
	source .venv/bin/activate && flask shell
	rm .env
