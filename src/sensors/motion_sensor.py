import time
import random
import json
import os
from datetime import datetime, timezone
from kafka import KafkaProducer
from prometheus_client import start_http_server, Gauge

# Define Prometheus metrics
motion_metric = Gauge('motion_sensor_value', 'Motion sensor value', ['sensor_id'])

def simulate_motion():
    return random.choice([0, 1])  # Simulate motion as 0 or 1 (boolean)

if __name__ == "__main__":
    sensor_id = "motion_1"
    start_http_server(8000)  # Expose metrics on port 8000
    while True:
        motion = simulate_motion()
        motion_metric.labels(sensor_id=sensor_id).set(motion)
        print(f"Motion: {motion}")
        time.sleep(1)

# Configurable Kafka settings
KAFKA_ENABLED = os.getenv("KAFKA_MOTION_ENABLED", "false").lower() == "true"
KAFKA_TOPIC = os.getenv("KAFKA_MOTION_TOPIC", "sensor.motion")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Retry config
MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

# Unique sensor ID
sensor_id = random.randint(1, 1000)

# Kafka producer setup (with retries)
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

if __name__ == "__main__":
    tick = 0
    while True:
        motion = simulate_motion()
        timestamp = datetime.now(timezone.utc).isoformat()

        sensor_data = {
            "timestamp": timestamp,
            "sensor_id": sensor_id,
            "sensor_type": "motion",
            "value": motion,
            "units": "boolean"
        }

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
