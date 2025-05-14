import time
import random
import json
import os
from datetime import datetime, timezone
from kafka import KafkaProducer
from prometheus_client import start_http_server, Counter, Gauge

# Configurable Kafka settings
KAFKA_ENABLED = os.getenv("KAFKA_HUMIDITY_ENABLED", "false").lower() == "true"
KAFKA_TOPIC = os.getenv("KAFKA_HUMIDITY_TOPIC", "sensor.humidity")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))

# Prometheus metrics
messages_sent = Counter("humidity_messages_sent_total", "Total humidity messages sent")
current_humidity = Gauge("humidity_value_percent", "Current humidity value in percent")

# Start metrics server
start_http_server(METRICS_PORT)
print(f"[Metrics] Prometheus metrics exposed on port {METRICS_PORT}")

# Retry config
MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

# Base humidity percentage (comfortable indoor level)
base_humidity = 45.0  # percent
sensor_id = random.randint(1, 1000)

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

def simulate_humidity(tick):
    drift = 10 * random.uniform(-1, 1) * (tick % 60) / 60
    noise = random.uniform(-2.0, 2.0)
    humidity = base_humidity + drift + noise
    return round(max(0, min(100, humidity)), 2)

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

        # Set Prometheus gauge
        current_humidity.set(humidity)

        if KAFKA_ENABLED and producer:
            try:
                producer.send(KAFKA_TOPIC, value=sensor_data)
                producer.flush()
                print(f"[Kafka] Sent to topic '{KAFKA_TOPIC}': {sensor_data}")
                messages_sent.inc()
            except Exception as e:
                print(f"[ERROR] Failed to send to Kafka: {e}")
        else:
            print(f"[Local] {json.dumps(sensor_data)}")

        tick += 1
        time.sleep(5)
