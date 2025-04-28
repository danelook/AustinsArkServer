# Docker/consumer/Dockerfile

FROM python:3.13-slim

WORKDIR /app

# Update OS packages and install pip (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*  

# Install dependencies
COPY ../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy consumer code
COPY ./src/consumer/kafka_consumer.py . 

CMD ["python", "kafka_consumer.py"]
