FROM python:alpine3.7
COPY requirements.txt /app/requirements.txt
COPY gateway /app
COPY nanotuya /app/nanotuya
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python ./gateway.py

EXPOSE 65080/tcp