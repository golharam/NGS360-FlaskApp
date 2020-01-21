#!/bin/bash

python -m pytest -vv --cov app/ --ignore=tests/FrontEnd && coverage html
