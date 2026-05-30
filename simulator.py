import requests
import time
import random

API = "http://127.0.0.1:8000"

while True:
    event = {
        "store_id": "STORE_001",
        "camera_id": random.choice(["CAM_1", "CAM_2", "CAM_3"]),
        "visitor_id": f"V{random.randint(1,10)}",
        "event_type": random.choices(
		["ENTRY", "EXIT"],
		weights=[0.7, 0.3]
	)[0]
    }

    try:
        requests.post(f"{API}/add-event", json=event)
        print("Event sent:", event)
    except:
        print("Server error")

    time.sleep(2)
