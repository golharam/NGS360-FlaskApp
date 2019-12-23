# FlaskApp
NGS 360 Front-End Web Application

## Motivation
We needed an easy way for everyone to access NGS data and pipelines.  This app provides that interface.

## Architecture
This app is deployed via Amazon Elastic BeanStalk as a Python Flask application in Docker.

This application was originally modeled after https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

## Configuration Settings
Default configuration settings are loaded from config.py, then can be overridden by setting the environment variable, NGS360_SETTINGS,
to the full path of a config file. Config files are python files and only values in uppercase are actually stored.  This provides a way
to maintain multiple app configurations external to the application.

## Build, Test, Run
Makefile targets are used to make this easy:
```
build - Build the Docker image for this app
test - Run unit tests (currently this is done on outside of Docker.  This may be a problem due to local host machine settings)
make - Run the app in Docker
```

## Development
NGS360 uses 'A successful Git branching model' for development:
  - Feature branches are forked from the develop branch
  - master branch is pushed into production
  - Branch names should be Jira ticket ids

We also aim to achieve https://12factor.net
