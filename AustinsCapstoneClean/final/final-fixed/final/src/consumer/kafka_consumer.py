import json
import mysql.connector
from kafka import KafkaConsumer

# Connect to MySQL
db = mysql.connector.connect(
    host="mysql",  # MUST match your Kubernetes service name
    user="sensoruser",
    password="sensorpass",
    database="sensordata"
)
cursor = db.cursor()

# Ensure the table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_type VARCHAR(255),
    value FLOAT,
    timestamp VARCHAR(255)
)
""")
db.commit()

# Create Kafka consumer subscribed to sensor topics
consumer = KafkaConsumer(
    'sensor.humidity',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("[Kafka Consumer] Started and waiting for messages...")

# Process incoming messages
for message in consumer:
    data = message.value
    print("[Kafka Consumer] Received message:", data)
    
    cursor.execute(
        "INSERT INTO readings (sensor_type, value, timestamp) VALUES (%s, %s, %s)",
        (
            data.get("sensor_type"),
            data.get("value"),
            data.get("timestamp")
        )
    )
    db.commit()

