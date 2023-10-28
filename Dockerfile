FROM mtr.devops.telekom.de/mcsps/python:3.10-slim
LABEL org.opencontainers.image.authors="caas-request@telekom.de"
LABEL version="1.0.0"
LABEL description="Python Flask Entsoe App"

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confnew vim-tiny python3-venv python3-dev net-tools libssl-dev curl libcurl4-openssl-dev gcc

COPY flask/app.py /home/appuser/app.py
COPY flask/wsgi.py /home/appuser/wsgi.py
COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser
ENV PYTHONUNBUFFERED=0
ENV WEBHOOKPORT=9091
ENTRYPOINT gunicorn --bind 0.0.0.0:${WEBHOOKPORT} --access-logfile /dev/stdout wsgi:app
