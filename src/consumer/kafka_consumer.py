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

def ensure_mysql_connection():
    global mysql_conn
    try:
        if not mysql_conn.is_connected():
            print("[Alert] MySQL connection lost. Attempting to reconnect...")
            mysql_conn = connect_mysql_with_retry()
    except Exception as e:
        print(f"[Critical] Error checking MySQL connection: {e}")
        mysql_conn = connect_mysql_with_retry()

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

def ensure_mongo_connection():
    global mongo_collection
    try:
        # Try a harmless operation to test connection
        mongo_collection.estimated_document_count()
    except Exception as e:
        print(f"[Alert] MongoDB connection lost. Attempting to reconnect... Reason: {e}")
        mongo_collection = connect_mongo_with_retry()

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

def ensure_kafka_connection(consumer):
    try:
        # Try to fetch metadata as a way to test if the connection is alive
        consumer.partitions_for_topic(KAFKA_TOPICS[0])  # You can replace with any topic
    except Exception as e:
        print(f"[Alert] Kafka connection lost. Attempting to reconnect... Reason: {e}")
        consumer.close()
        consumer = connect_kafka_with_retry()
        print("[Kafka] Reconnected successfully.")
    return consumer

# Establish connections
mysql_conn = connect_mysql_with_retry()
mongo_collection = connect_mongo_with_retry()
consumer = connect_kafka_with_retry()

print(f"[Consumer] Listening to topics: {KAFKA_TOPICS}")

try:
    for message in consumer:
        # Ensure Kafka connection before processing messages
        consumer = ensure_kafka_connection(consumer)

        # Process messages as usual
        data = message.value
        topic = message.topic
        print(f"[Received] Topic: {topic} | Data: {data}")

        ensure_mongo_connection()
        if topic == "server.logs":
            try:
                mongo_collection.insert_one(data)
                print("[MongoDB] Inserted log into MongoDB")
            except Exception as e:
                print(f"[MongoDB ERROR] Failed to insert log after reconnect attempt: {e}")
                print(f"[Monitoring] ALERT: MongoDB insert failure for topic '{topic}' with data {data}")
            continue

        ensure_mysql_connection()
        sensor_type = data.get("sensor_type")
        timestamp = data.get("timestamp")
        sensor_id = data.get("sensor_id")
        value = data.get("value")
        units = data.get("units")

        try:
            cursor = mysql_conn.cursor()

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
            print(f"[MySQL] Inserted {sensor_type} data successfully.")

        except Error as e:
            print(f"[MySQL ERROR] Failed to insert {sensor_type} reading: {e}")
            print(f"[Monitoring] ALERT: MySQL insert failure for topic '{topic}' with data {data}")
        finally:
            if 'cursor' in locals():
                cursor.close()

except KeyboardInterrupt:
    print("\n[Consumer] Shutting down...")
finally:
    consumer.close()
    if mysql_conn.is_connected():
        mysql_conn.close()
