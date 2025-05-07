CREATE DATABASE IF NOT EXISTS sensordata;

USE sensordata;

CREATE TABLE IF NOT EXISTS sensor_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    sensor_id INT NOT NULL,
    sensor_type VARCHAR(50),
    value VARCHAR(255),
    units VARCHAR(20)
);
