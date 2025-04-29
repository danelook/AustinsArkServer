import time
import random
import math
from datetime import datetime, timezone
import json
import os
from kafka import KafkaProducer

KAFKA_ENABLED = os.getenv("KAFKA_TEMP_ENABLED", "false").lower() == "true"
KAFKA_TOPIC = os.getenv("KAFKA_TEMP_TOPIC", "sensor.temperature")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

base_temp_f = 72.0
sensor_id = random.randint(1, 1000)

MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

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

def simulate_temperature(tick):
    daily_drift = 9 * math.sin(2 * math.pi * (tick % 60) / 60)
    random_noise = random.uniform(-1.0, 1.0)
    return round(base_temp_f + daily_drift + random_noise, 2)

if __name__ == "__main__":
    tick = 0
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        temp_f = simulate_temperature(tick)

        sensor_data = {
            "timestamp": timestamp,
            "sensor_id": sensor_id,
            "sensor_type": "temperature",
            "value": temp_f,
            "units": "F"
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
