FROM python:3.7-slim

RUN apt-get update && \
    apt-get upgrade -y

WORKDIR "/buildkite"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/generate_pipeline.py /usr/local/bin/

CMD ["generate_pipeline.py"]