FROM python:3.7-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

WORKDIR "/buildkite"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "scripts/generate_pipeline.py"]