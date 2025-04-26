FROM python:3.9-slim

WORKDIR /app

COPY ../../../../src/sensors/humidity_sensor.py .

CMD ["python", "humidity_sensor.py"]

# To build image: 
    # docker build -t humidity_sensor:latest -f Docker/sensors/humidity/Dockerfile .