from kafka import KafkaConsumer
import json
import os
import time
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from prometheus_client import start_http_server, Counter

# Prometheus metrics
SENSOR_MESSAGES_TOTAL = Counter("sensor_messages_total", "Number of messages processed per sensor type", ["sensor_type"])
LOG_INSERTS_TOTAL = Counter("log_inserts_total", "Number of log inserts into MongoDB")
MYSQL_INSERT_FAILURES = Counter("mysql_insert_failures_total", "MySQL insert failures", ["sensor_type"])
MONGO_INSERT_FAILURES = Counter("mongo_insert_failures_total", "MongoDB insert failures")

start_http_server(8000)

# Kafka Configuration
KAFKA_TOPICS = os.getenv("KAFKA_TOPICS", "sensor.temperature,sensor.humidity,sensor.motion,server.logs").split(",")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "sensor-consumer-group")

# MySQL Configuration
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "password"),
    "database": os.getenv("MYSQL_DATABASE", "sensordata")
}

# MongoDB Configuration
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "logdata")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "server_logs")

def connect_mysql_with_retry(retries=10, delay=5):
    for attempt in range(retries):
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            print("[MySQL] Connected")
            return conn
        except Error as e:
            print(f"[MySQL] Connection failed (attempt {attempt + 1}): {e}")
            time.sleep(delay)
    raise Exception("Failed to connect to MySQL")

def connect_mongo_with_retry(retries=10, delay=5):
    for attempt in range(retries):
        try:
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            print("[MongoDB] Connected")
            return client[MONGO_DB][MONGO_COLLECTION]
        except Exception as e:
            print(f"[MongoDB] Connection failed (attempt {attempt + 1}): {e}")
            time.sleep(delay)
    raise Exception("Failed to connect to MongoDB")

def connect_kafka_with_retry(retries=10, delay=5):
    for attempt in range(retries):
        try:
            consumer = KafkaConsumer(
                *KAFKA_TOPICS,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                group_id=KAFKA_GROUP_ID,
                auto_offset_reset="earliest"
            )
            print("[Kafka] Connected and subscribed")
            return consumer
        except Exception as e:
            print(f"[Kafka] Connection failed (attempt {attempt + 1}): {e}")
            time.sleep(delay)
    raise Exception("Failed to connect to Kafka")

mysql_conn = connect_mysql_with_retry()
mongo_collection = connect_mongo_with_retry()
consumer = connect_kafka_with_retry()

try:
    for message in consumer:
        topic = message.topic
        data = message.value
        print(f"[Received] {topic}: {data}")

        if topic == "server.logs":
            try:
                mongo_collection.insert_one(data)
                LOG_INSERTS_TOTAL.inc()
                print("[MongoDB] Log inserted")
            except Exception as e:
                MONGO_INSERT_FAILURES.inc()
                print(f"[MongoDB ERROR] Insert failed: {e}")
            continue

        sensor_type = data.get("sensor_type")
        timestamp = data.get("timestamp")
        sensor_id = data.get("sensor_id")
        value = data.get("value")
        units = data.get("units")

        if sensor_type not in ["temperature", "humidity", "motion"]:
            print(f"[Warning] Unknown sensor type: {sensor_type}")
            continue

        try:
            cursor = mysql_conn.cursor()

            insert_query = f"""
                INSERT INTO {sensor_type}_readings (timestamp, sensor_id, value, units)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(insert_query, (timestamp, sensor_id, value, units))
            mysql_conn.commit()
            SENSOR_MESSAGES_TOTAL.labels(sensor_type=sensor_type).inc()
            print(f"[MySQL] {sensor_type} data inserted")

        except Error as e:
            MYSQL_INSERT_FAILURES.labels(sensor_type=sensor_type).inc()
            print(f"[MySQL ERROR] Failed to insert {sensor_type} data: {e}")

        finally:
            if 'cursor' in locals():
                cursor.close()

except KeyboardInterrupt:
    print("\n[Consumer] Shutdown requested")
finally:
    consumer.close()
    if mysql_conn.is_connected():
        mysql_conn.close()
