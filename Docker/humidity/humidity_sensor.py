import time
import random
from datetime import datetime, timezone
import json

# Base humidity percentage (comfortable indoor level)
base_humidity = 45.0  # percent

# Generate a unique sensor ID for this humidity sensor
sensor_id = random.randint(1, 1000)

def simulate_humidity(tick):
    """
    Simulate a fluctuating humidity level (%).
    Uses sine-based drift and random noise.
    """
    drift = 10 * random.uniform(-1, 1) * (tick % 60) / 60
    noise = random.uniform(-2.0, 2.0)
    humidity = base_humidity + drift + noise
    humidity = max(0, min(100, humidity))  # Clamp to valid % range
    return round(humidity, 2)

if __name__ == "__main__":
    tick = 0
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        humidity = simulate_humidity(tick)

        sensor_data = {
            "timestamp": timestamp,
            "sensor_id": sensor_id,
            "sensor_type": "humidity",
            "value": humidity,
            "units": "%"
        }

        # Serialize and print (for now)
        sensor_data_json = json.dumps(sensor_data)
        print(sensor_data_json)

        tick += 1
        time.sleep(1)
