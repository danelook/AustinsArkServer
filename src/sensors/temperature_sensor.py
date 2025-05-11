import time
import random
import math
from datetime import datetime, timezone
import json
import os
from kafka import KafkaProducer
from prometheus_client import start_http_server, Gauge

# Define Prometheus metrics for temperature
temperature_metric = Gauge('temperature_sensor_value', 'Temperature sensor value', ['sensor_id'])

# Configurable Kafka settings
KAFKA_ENABLED = os.getenv("KAFKA_TEMP_ENABLED", "false").lower() == "true"
KAFKA_TOPIC = os.getenv("KAFKA_TEMP_TOPIC", "sensor.temperature")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Base temperature in Fahrenheit
base_temp_f = 72.0
sensor_id = random.randint(1, 1000)

# Retry config for Kafka
MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

# Kafka producer setup (if enabled)
producer = None
if KAFKA_ENABLED:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print(f"[Producer] Connected to Kafka on attempt {attempt}")
            break
        except Exception as e:
            print(f"[Retry {attempt}] Failed to connect to Kafka: {e}")
            time.sleep(RETRY_DELAY)

    if not producer:
        print("[Producer] Could not connect to Kafka. Disabling Kafka output.")
        KAFKA_ENABLED = False

# Function to simulate temperature readings
def simulate_temperature(tick):
    daily_drift = 9 * math.sin(2 * math.pi * (tick % 60) / 60)
    random_noise = random.uniform(-1.0, 1.0)
    return round(base_temp_f + daily_drift + random_noise, 2)

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8002)  # Expose metrics on port 8002

    tick = 0
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        temp_f = simulate_temperature(tick)

        # Update Prometheus metric
        temperature_metric.labels(sensor_id=sensor_id).set(temp_f)

        # Prepare sensor data
        sensor_data = {
            "timestamp": timestamp,
            "sensor_id": sensor_id,
            "sensor_type": "temperature",
            "value": temp_f,
            "units": "F"
        }

        # Send data to Kafka if enabled
        if KAFKA_ENABLED and producer:
            try:
                producer.send(KAFKA_TOPIC, value=sensor_data)
                producer.flush()
                print(f"[Kafka] Sent to topic '{KAFKA_TOPIC}': {sensor_data}")
            except Exception as e:
                print(f"[ERROR] Failed to send to Kafka: {e}")
        else:
            print(f"[Local] {json.dumps(sensor_data)}")

        tick += 1
        time.sleep(1)
