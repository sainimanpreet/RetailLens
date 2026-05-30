from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
def home():
    return {"message": "RetailLens API running"}

@app.get("/events")
def get_events():
    events = []
    try:
        with open("events.jsonl", "r") as file:
            for line in file:
                events.append(json.loads(line))
    except FileNotFoundError:
        return {"error": "No events file found"}

    return {"events": events}


@app.get("/metrics")
def get_metrics():
    total_entries = 0
    total_exits = 0

    try:
        with open("events.jsonl", "r") as file:
            for line in file:
                event = json.loads(line)

                if event["event_type"] == "ENTRY":
                    total_entries += 1
                elif event["event_type"] == "EXIT":
                    total_exits += 1

    except FileNotFoundError:
        return {"error": "No events file found"}

    return {
        "total_entries": total_entries,
        "total_exits": total_exits,
        "current_inside": total_entries - total_exits
    }


@app.get("/funnel")
def get_funnel():
    entries = set()
    exits = set()

    try:
        with open("events.jsonl", "r") as file:
            for line in file:
                event = json.loads(line)

                if event["event_type"] == "ENTRY":
                    entries.add(event["visitor_id"])
                elif event["event_type"] == "EXIT":
                    exits.add(event["visitor_id"])

    except FileNotFoundError:
        return {"error": "No events file found"}

    total_entered = len(entries)
    total_exited = len(exits)

    conversion_rate = 0
    if total_entered > 0:
        conversion_rate = ((total_entered - total_exited) / total_entered) * 100

    return {
        "total_entered": total_entered,
        "total_exited": total_exited,
        "conversion_rate": round(conversion_rate, 2)
    }


# 🔥 ADDED: Average Dwell Time
@app.get("/dwell")
def get_dwell():
    total_dwell = 0
    count = 0

    try:
        with open("events.jsonl", "r") as file:
            for line in file:
                event = json.loads(line)

                if event["event_type"] == "EXIT":
                    total_dwell += event.get("dwell_ms", 0)
                    count += 1

    except FileNotFoundError:
        return {"error": "No events file found"}

    avg_dwell = total_dwell / count if count > 0 else 0

    return {
        "average_dwell_ms": avg_dwell,
        "average_dwell_seconds": round(avg_dwell / 1000, 2)
    }


# 🔥 ADDED: Camera-wise Metrics
@app.get("/camera-metrics")
def camera_metrics():
    data = {}

    try:
        with open("events.jsonl", "r") as file:
            for line in file:
                event = json.loads(line)
                cam = event.get("camera_id", "unknown")

                if cam not in data:
                    data[cam] = {
                        "entries": 0,
                        "exits": 0
                    }

                if event["event_type"] == "ENTRY":
                    data[cam]["entries"] += 1
                elif event["event_type"] == "EXIT":
                    data[cam]["exits"] += 1

    except FileNotFoundError:
        return {"error": "No events file found"}

    return data