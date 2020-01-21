FROM python:3
MAINTAINER Ryan Golhar "ryan.golhar@bms.com"

WORKDIR /app

COPY application.py boot.sh config.py requirements.txt /app/
COPY app/ /app/app/
COPY migrations /app/migrations/

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["boot.sh"]
