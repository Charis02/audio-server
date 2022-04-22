FROM python:latest
ADD . /app
WORKDIR /app
RUN python3 -m pip install -r requirements.txt