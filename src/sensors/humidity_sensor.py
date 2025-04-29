import time
import random
import json
import os
from datetime import datetime, timezone
from kafka import KafkaProducer

# Configurable Kafka settings
KAFKA_ENABLED = os.getenv("KAFKA_HUMIDITY_ENABLED", "false").lower() == "true"
KAFKA_TOPIC = os.getenv("KAFKA_HUMIDITY_TOPIC", "sensor.humidity")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Base humidity percentage (comfortable indoor level)
base_humidity = 45.0  # percent

# Generate a unique sensor ID for this humidity sensor
sensor_id = random.randint(1, 1000)

# Kafka producer setup (if enabled)
producer = None
if KAFKA_ENABLED:
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
    except Exception as e:
        print(f"[ERROR] Failed to connect to Kafka: {e}")
        KAFKA_ENABLED = False

def simulate_humidity(tick):
    """
    Simulate a fluctuating humidity level (%).
    Uses sine-based drift and random noise.
    """
    drift = 10 * random.uniform(-1, 1) * (tick % 60) / 60
    noise = random.uniform(-2.0, 2.0)
    humidity = base_humidity + drift + noise
    humidity = max(0, min(100, humidity))  # Clamp to valid % range
    return round(humidity, 2)

if __name__ == "__main__":
    tick = 0
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        humidity = simulate_humidity(tick)

        sensor_data = {
            "timestamp": timestamp,
            "sensor_id": sensor_id,
            "sensor_type": "humidity",
            "value": humidity,
            "units": "%"
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
