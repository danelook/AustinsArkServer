import time
import random
import json
from datetime import datetime, timezone

# Unique sensor ID
sensor_id = random.randint(1, 1000)

def simulate_motion():
    """
    Randomly decide if motion is detected (10% chance).
    """
    return random.random() < 0.1

if __name__ == "__main__":
    tick = 0
    while True:
        motion = simulate_motion()
        timestamp = datetime.now(timezone.utc).isoformat()

        sensor_data = {
            "timestamp": timestamp,
            "sensor_id": sensor_id,
            "sensor_type": "motion",
            "value": motion,
            "units": "boolean"
        }

        sensor_data_json = json.dumps(sensor_data)
        print(sensor_data_json)

        tick += 1
        time.sleep(1)
