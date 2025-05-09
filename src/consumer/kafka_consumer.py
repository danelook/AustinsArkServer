from kafka import KafkaConsumer
import json
import os
import time
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient

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

# MongoDB config
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "logdata")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "server_logs")

MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

def connect_mysql_with_retry():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
            if conn.is_connected():
                print(f"[MySQL] Connected successfully on attempt {attempt}")
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"[MySQL] Test query result: {result}")
                cursor.close()
                return conn
        except Error as e:
            print(f"[Retry {attempt}] MySQL connection failed: {e}")
        time.sleep(RETRY_DELAY)
    print("[MySQL] Could not connect after retries. Exiting.")
    exit(1)

def connect_mongo_with_retry():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            print(f"[MongoDB] Connected successfully on attempt {attempt}")
            return collection
        except Exception as e:
            print(f"[Retry {attempt}] MongoDB connection failed: {e}")
        time.sleep(RETRY_DELAY)
    print("[MongoDB] Could not connect after retries. Exiting.")
    exit(1)

def connect_kafka_with_retry():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            consumer = KafkaConsumer(
                *KAFKA_TOPICS,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=KAFKA_GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True
            )
            print(f"[Kafka] Connected on attempt {attempt}")
            return consumer
        except Exception as e:
            print(f"[Retry {attempt}] Kafka connection failed: {e}")
        time.sleep(RETRY_DELAY)
    print("[Kafka] Could not connect after retries. Exiting.")
    exit(1)

# Establish connections
mysql_conn = connect_mysql_with_retry()
mongo_collection = connect_mongo_with_retry()
consumer = connect_kafka_with_retry()

print(f"[Consumer] Listening to topics: {KAFKA_TOPICS}")

try:
    for message in consumer:
        sensor_data = message.value
        topic = message.topic
        print(f"[Received] Topic: {topic} | Data: {sensor_data}")

        if topic == "server.logs":
            try:
                mongo_collection.insert_one(sensor_data)
                print("[MongoDB] Inserted log into MongoDB")
            except Exception as e:
                print(f"[MongoDB ERROR] Failed to insert log: {e}")
            continue

        # Insert sensor data into MySQL
        cursor = mysql_conn.cursor()

        sensor_type = sensor_data.get("sensor_type")
        timestamp = sensor_data.get("timestamp")
        sensor_id = sensor_data.get("sensor_id")
        value = sensor_data.get("value")
        units = sensor_data.get("units")

        try:
            if sensor_type == "motion":
                insert_query = """
                    INSERT INTO motion_readings (timestamp, sensor_id, value, units)
                    VALUES (%s, %s, %s, %s)
                """
            elif sensor_type == "temperature":
                insert_query = """
                    INSERT INTO temperature_readings (timestamp, sensor_id, value, units)
                    VALUES (%s, %s, %s, %s)
                """
            elif sensor_type == "humidity":
                insert_query = """
                    INSERT INTO humidity_readings (timestamp, sensor_id, value, units)
                    VALUES (%s, %s, %s, %s)
                """
            else:
                print(f"[Warning] Unknown sensor type: {sensor_type}. Skipping insert.")
                continue

            cursor.execute(insert_query, (timestamp, sensor_id, value, units))
            mysql_conn.commit()
        except Exception as e:
            print(f"[MySQL ERROR] Failed to insert {sensor_type} reading: {e}")
        finally:
            cursor.close()

except KeyboardInterrupt:
    print("\n[Consumer] Shutting down...")
finally:
    consumer.close()
    if mysql_conn.is_connected():
        mysql_conn.close()
