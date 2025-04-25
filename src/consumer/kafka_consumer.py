from kafka import KafkaConsumer
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Kafka settings from .env
KAFKA_TOPIC = os.getenv("KAFKA_TEMP_TOPIC", "sensor.temperature")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "sensor-consumer-group")

# Create Kafka consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id=KAFKA_GROUP_ID,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",  # start from beginning if no committed offset
    enable_auto_commit=True
)

print(f"[Consumer] Listening to topic '{KAFKA_TOPIC}'...")

try:
    for message in consumer:
        sensor_data = message.value
        print(f"[Received] {sensor_data}")
except KeyboardInterrupt:
    print("\n[Consumer] Shutting down...")
finally:
    consumer.close()
