FROM python:alpine3.7
COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python ./gateway/gateway.py

EXPOSE 65080/tcp