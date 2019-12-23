FROM python:3-alpine
MAINTAINER Ryan Golhar "ryan.golhar@bms.com"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "application.py"]
