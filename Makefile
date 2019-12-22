NAME=ngs360-flaskapp
.PHONY: build test run clean

clean:
	rm -rf .coverage .pytest_cache/ __pycache__/ htmlcov/

build:
	docker build -t $(NAME) .

test: build
	docker run --rm $(NAME) python -m pytest tests/

run: build
	docker run --rm -t -p 5000:5000 $(NAME)

