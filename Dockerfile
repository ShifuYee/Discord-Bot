FROM python:alpine3.6

COPY . /app
WORKDIR /app

RUN python setup.py install
RUN python -m unittest discover
