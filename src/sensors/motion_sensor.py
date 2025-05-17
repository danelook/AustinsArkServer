import time
import random
import json
import os
from datetime import datetime, timezone
from kafka import KafkaProducer
from prometheus_client import start_http_server, Counter, Gauge

# Configurable settings
KAFKA_ENABLED = os.getenv("KAFKA_MOTION_ENABLED", "false").lower() == "true"
KAFKA_TOPIC = os.getenv("KAFKA_MOTION_TOPIC", "sensor.motion")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))

# Prometheus metrics
messages_sent = Counter("motion_messages_sent_total", "Total motion messages sent")
motion_events = Counter("motion_events_detected_total", "Total motion events detected")
current_motion = Gauge("motion_detected", "Current motion detection status (1=motion, 0=no motion)")

# Start Prometheus metrics server
start_http_server(METRICS_PORT)
print(f"[Metrics] Prometheus metrics exposed on port {METRICS_PORT}")

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

def simulate_motion():
    return random.random() < 0.1  # 10% chance of motion

if __name__ == "__main__":
    tick = 0
    while True:
        motion = simulate_motion()
        timestamp = datetime.now(timezone.utc).isoformat()

        # Prometheus updates
        current_motion.set(1 if motion else 0)
        if motion:
            motion_events.inc()

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
                messages_sent.inc()
            except Exception as e:
                print(f"[ERROR] Failed to send to Kafka: {e}")
        else:
            print(f"[Local] {json.dumps(sensor_data)}")

        tick += 1
        time.sleep(5)
