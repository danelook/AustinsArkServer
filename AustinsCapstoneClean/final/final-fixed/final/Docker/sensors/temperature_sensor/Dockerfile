FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY temperature_sensor.py .

CMD ["python", "temperature_sensor.py"]