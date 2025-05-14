CREATE DATABASE IF NOT EXISTS sensordata;

USE sensordata;

-- Motion sensor table
CREATE TABLE IF NOT EXISTS motion_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    sensor_id INT NOT NULL,
    value BOOLEAN,
    units VARCHAR(20)
);

-- Temperature sensor table
CREATE TABLE IF NOT EXISTS temperature_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    sensor_id INT NOT NULL,
    value FLOAT,
    units VARCHAR(20)
);

-- Humidity sensor table
CREATE TABLE IF NOT EXISTS humidity_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    sensor_id INT NOT NULL,
    value FLOAT,
    units VARCHAR(20)
);
