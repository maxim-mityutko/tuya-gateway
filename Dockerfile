FROM python:alpine3.7
COPY requirements.txt /app/requirements.txt
COPY gateway /app
COPY nanotuya /app/nanotuya
WORKDIR /app

RUN apk add build-base
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apk del build-base

CMD python ./gateway.py

EXPOSE 65080/tcp