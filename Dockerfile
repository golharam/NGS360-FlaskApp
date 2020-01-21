FROM python:3
MAINTAINER Ryan Golhar "ryan.golhar@bms.com"

WORKDIR /app

COPY requirements.txt requirements-dev.txt /app/
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY application.py boot.sh config.py test.sh /app/
COPY app/ /app/app/
COPY migrations /app/migrations/
COPY tests /app/tests/

EXPOSE 5000
CMD ["boot.sh"]
