from kafka import KafkaConsumer
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

KAFKA_TOPIC = os.getenv("KAFKA_TEMP_TOPIC", "sensor.temperature")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "sensor-consumer-group")

MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

consumer = None
for attempt in range(1, MAX_RETRIES + 1):
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=KAFKA_GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True
        )
        print(f"[Consumer] Connected to Kafka on attempt {attempt}")
        break
    except Exception as e:
        print(f"[Retry {attempt}] Failed to connect to Kafka: {e}")
        time.sleep(RETRY_DELAY)

if not consumer:
    print("[Consumer] Could not connect to Kafka after retries. Exiting.")
    exit(1)

print(f"[Consumer] Listening to topic '{KAFKA_TOPIC}'...")

try:
    for message in consumer:
        sensor_data = message.value
        print(f"[Received] {sensor_data}")
except KeyboardInterrupt:
    print("\n[Consumer] Shutting down...")
finally:
    consumer.close()
