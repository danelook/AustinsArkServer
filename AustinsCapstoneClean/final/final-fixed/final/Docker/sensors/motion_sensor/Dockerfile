FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY motion_sensor.py .

CMD ["python", "motion_sensor.py"]