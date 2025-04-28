import time
import random
import json
import os
from datetime import datetime, timezone
from kafka import KafkaProducer

# Configurable Kafka settings
KAFKA_ENABLED = os.getenv("KAFKA_MOTION_ENABLED", "false").lower() == "true"
KAFKA_TOPIC = os.getenv("KAFKA_MOTION_TOPIC", "sensor.motion")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Unique sensor ID
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

def simulate_motion():
    """
    Randomly decide if motion is detected (10% chance).
    """
    return random.random() < 0.1

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
