import mysql.connector
import csv

# MySQL connection
db = mysql.connector.connect(
    host="127.0.0.1",
    user="sensoruser",
    password="sensorpass",
    database="sensordata"
)
cursor = db.cursor()

# Ensure table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_type VARCHAR(255),
    value FLOAT,
    timestamp VARCHAR(255)
)
""")
db.commit()

# Query all readings
cursor.execute("SELECT * FROM readings")
results = cursor.fetchall()

# Export to CSV only if data exists
if cursor.description is None or not results:
    print("No data found in 'readings' table. Nothing exported.")
else:
    with open('readings.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([i[0] for i in cursor.description])  # write headers
        writer.writerows(results)
    print(f"Exported {len(results)} rows to readings.csv")

cursor.close()
db.close()

