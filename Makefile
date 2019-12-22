NAME=ngs360-flaskapp
.PHONY: build test run

build:
	docker build -t $(NAME) .

test: build
	docker run --rm $(NAME) python -m pytest tests/

run: build
	docker run --rm -t -p 5000:5000 $(NAME)

