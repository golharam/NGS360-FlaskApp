FROM python:3
MAINTAINER Ryan Golhar "ryan.golhar@bms.com"

WORKDIR /app

COPY requirements.txt requirements-dev.txt /app/
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY application.py config.py boot.sh test.sh /app/
COPY app/ /app/app/
COPY migrations /app/migrations/
COPY tests /app/tests/
COPY test_data /app/test_data/

EXPOSE 5000
CMD ["./boot.sh"]
