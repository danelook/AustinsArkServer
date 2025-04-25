import time
import random
import math
from datetime import datetime, timezone
import json

# Starting temperature in Fahrenheit
base_temp_f = 72.0

# Create a random Sensor_ID
sensor_id = random.randint(1, 1000)

def simulate_temperature(tick):
    """
    Simulate a fluctuating temperature in Fahrenheit.
    """
    daily_drift = 9 * math.sin(2 * math.pi * (tick % 60) / 60)
    random_noise = random.uniform(-1.0, 1.0)
    temperature = base_temp_f + daily_drift + random_noise
    return round(temperature, 2)

if __name__ == "__main__":
    tick = 0
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        temp_f = simulate_temperature(tick)

        sensor_data = {
            "timestamp": timestamp,
            "sensor_id": sensor_id,
            "sensor_type": "temperature",
            "value": temp_f,
            "units": "F"
        }

        # Serialize to JSON (optional here, but required for Kafka later)
        sensor_data_json = json.dumps(sensor_data)

        # For now, just print the structured data (this will be replaced by Kafka send)
        print(sensor_data_json)

        tick += 1
        time.sleep(1)
