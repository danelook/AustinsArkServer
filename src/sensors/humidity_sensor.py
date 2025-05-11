import time
import random
import json
import os
from datetime import datetime, timezone
from kafka import KafkaProducer
from prometheus_client import start_http_server, Gauge
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define Prometheus metric
HUMIDITY_METRIC = Gauge('humidity_sensor_value', 'Humidity sensor value', ['sensor_id'])

# Sensor simulation parameters
BASE_HUMIDITY = 45.0  # Comfortable indoor level (%)
SENSOR_ID = random.randint(1, 1000)

def simulate_humidity(tick=0):
    """Simulates humidity with drift and noise."""
    drift = 10 * random.uniform(-1, 1) * (tick % 60) / 60
    noise = random.uniform(-2.0, 2.0)
    humidity = BASE_HUMIDITY + drift + noise
    return round(max(0, min(100, humidity)), 2)

# Kafka Configuration from Environment Variables
KAFKA_ENABLED = os.getenv("KAFKA_HUMIDITY_ENABLED", "false").lower() == "true"
KAFKA_TOPIC = os.getenv("KAFKA_HUMIDITY_TOPIC", "sensor.humidity")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Kafka Retry Configuration
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

# Initialize Kafka producer (only if enabled)
producer = None
if KAFKA_ENABLED:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            logging.info("[Kafka] Producer initialized successfully.")
            break
        except Exception as e:
            logging.warning(f"[Retry {attempt}/{MAX_RETRIES}] Failed to connect to Kafka: {e}")
            time.sleep(RETRY_DELAY)
    if not producer:
        logging.error(f"[Kafka] Failed to initialize producer: {e}")
        KAFKA_ENABLED = None

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8001)
    logging.info("Prometheus metrics server started on port 8001")

    tick = 0
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        humidity = simulate_humidity(tick)

        # Update Prometheus metric
        HUMIDITY_METRIC.labels(sensor_id=SENSOR_ID).set(humidity)

        # Prepare sensor data payload
        sensor_data = {
            "timestamp": timestamp,
            "sensor_id": SENSOR_ID,
            "sensor_type": "humidity",
            "value": humidity,
            "units": "%"
        }

        # Send data to Kafka if enabled and producer is available
        if KAFKA_ENABLED and producer:
            try:
                producer.send(KAFKA_TOPIC, value=sensor_data)
                producer.flush()  # Ensure data is sent immediately
                logging.info(f"[Kafka] Sent to topic '{KAFKA_TOPIC}': {sensor_data}")
            except Exception as e:
                logging.error(f"[Kafka] Error sending data: {e}")
        else:
            logging.info(f"[Local] {json.dumps(sensor_data)}")

        tick += 1
        time.sleep(1)
