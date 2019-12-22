FROM python:3-alpine

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

EXPOSE 5000
CMD ["python", "application.py"]
