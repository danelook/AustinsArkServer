import time
import random
import json
import os
from datetime import datetime, timezone
from kafka import KafkaProducer
from prometheus_client import start_http_server, Counter, Gauge

# Kafka Config
KAFKA_ENABLED = os.getenv("KAFKA_LOG_ENABLED", "false").lower() == "true"
KAFKA_TOPIC = os.getenv("KAFKA_LOG_TOPIC", "server.logs")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))

# Log simulation parameters
LOG_LEVELS = ["INFO", "WARN", "ERROR"]
COMPONENTS = ["auth", "db", "api", "cache", "frontend"]

# Prometheus metrics
total_logs_sent = Counter("logs_sent_total", "Total number of log events sent")
log_level_counter = Counter("log_level_events_total", "Count of log events by level", ["level"])
latest_log_level = Gauge("latest_log_level", "Numerical value of last log level (INFO=0, WARN=1, ERROR=2)")

level_to_value = {"INFO": 0, "WARN": 1, "ERROR": 2}

# Start Prometheus metrics server
start_http_server(METRICS_PORT)
print(f"[Metrics] Prometheus metrics exposed on port {METRICS_PORT}")

producer = None
MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

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

def generate_log():
    level = random.choices(LOG_LEVELS, weights=[0.7, 0.2, 0.1])[0]
    log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "component": random.choice(COMPONENTS),
        "message": random.choice([
            "User login successful",
            "Database connection failed",
            "Cache miss for key session_123",
            "API timeout on GET /users",
            "Memory usage exceeded threshold",
            "Unauthorized access attempt"
        ])
    }
    return log

if __name__ == "__main__":
    while True:
        log_event = generate_log()
        level = log_event["level"]

        # Prometheus updates
        total_logs_sent.inc()
        log_level_counter.labels(level=level).inc()
        latest_log_level.set(level_to_value.get(level, -1))

        if KAFKA_ENABLED and producer:
            try:
                producer.send(KAFKA_TOPIC, value=log_event)
                producer.flush()
                print(f"[Kafka] Sent to topic '{KAFKA_TOPIC}': {log_event}")
            except Exception as e:
                print(f"[ERROR] Failed to send to Kafka: {e}")
        else:
            print(f"[Local] {json.dumps(log_event)}")

        time.sleep(random.uniform(5, 10))  # simulate varied log rate
