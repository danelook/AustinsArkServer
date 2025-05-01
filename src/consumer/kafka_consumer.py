from kafka import KafkaConsumer
import json
import os
import time 
import mysql.connector
from mysql.connector import Error

# Kafka config
KAFKA_TOPICS = os.getenv("KAFKA_TOPICS", "sensor.temperature").split(",")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "sensor-consumer-group")

# MySQL config
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "sensoruser")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "sensorpass")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "sensordata")

MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds 

def test_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        if conn.is_connected():
            print("[MySQL] Connection successful.")
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"[MySQL] Test query result: {result}")
            cursor.close()
            conn.close()
        else:
            print("[MySQL] Connection failed.")
    except Error as e:
        print(f"[MySQL ERROR] {e}")

test_mysql_connection()

consumer = None
for attempt in range(1, MAX_RETRIES + 1):
    try:
        consumer = KafkaConsumer(
            *KAFKA_TOPICS,  # Unpack topic list
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

print(f"[Consumer] Listening to topics: {KAFKA_TOPICS}")

try:
    for message in consumer:
        sensor_data = message.value
        topic = message.topic
        print(f"[Received] Topic: {topic} | Data: {sensor_data}")
except KeyboardInterrupt:
    print("\n[Consumer] Shutting down...")
finally:
    consumer.close()
