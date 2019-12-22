# FlaskApp
NGS 360 Front-End Web Application

## Motivation
We needed an easy way for everyone to access NGS data and pipelines.  This app provides that interface.

## Architecture
This app is deployed via Amazon Elastic BeanStalk as a Python Flask application in Docker.

This application was originally modeled after https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

## Build, Test, Run
Makefile targets are used to make this easy:
```
make build
make test
make run
```
