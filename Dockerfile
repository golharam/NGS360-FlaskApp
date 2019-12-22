FROM python:3-alpine
MAINTAINER Ryan Golhar "ryan.golhar@bms.com"

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements-dev.txt /app/requirements-dev.txt
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY . /app

EXPOSE 5000
CMD ["python", "application.py"]
