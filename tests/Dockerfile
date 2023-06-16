FROM python:3.7-slim-bullseye

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

WORKDIR "/buildkite"

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
