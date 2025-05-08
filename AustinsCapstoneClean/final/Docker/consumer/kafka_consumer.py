import mysql.connector
from kafka import KafkaConsumer
import json

# MySQL connection
db = mysql.connector.connect(
    host="mysql",
    user="sensoruser",
    password="sensorpass",
    database="sensordata"
)
cursor = db.cursor()

# Kafka consumer
consumer = KafkaConsumer(
    'sensor.humidity',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Ensure the readings table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_type VARCHAR(255),
    value FLOAT,
    timestamp VARCHAR(255)
)
""")
db.commit()

# Consume and insert messages
for message in consumer:
    data = message.value
    print("Received message:", data)
    cursor.execute(
        "INSERT INTO readings (sensor_type, value, timestamp) VALUES (%s, %s, %s)",
        (data.get("sensor_type"), data.get("value"), data.get("timestamp"))
    )
    db.commit()
