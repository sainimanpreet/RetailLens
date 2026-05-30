print("NEW CODE LOADED")
from typing import List
from fastapi import FastAPI
import json
from pydantic import BaseModel
from datetime import datetime
import uuid
import csv

app = FastAPI()
event_store = []
event_ids = set()
@app.get("/health")
def health_check():
    return {"status": "ok"}

class Event(BaseModel):
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: str  # ENTRY or EXIT

# Read events file
def read_events():
    events = []
    try:
        with open("events.jsonl", "r") as f:
            for line in f:
                events.append(json.loads(line))
    except Exception as e:
        return {"error": str(e)}
    return events
def read_pos():
    transactions = []
    try:
        with open("pos_transactions.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                transactions.append(row)
    except:
        return []
    return transactions
def get_all_events():
    file_events = read_events()
    if isinstance(file_events, dict):
        file_events = []

    return file_events + event_store


@app.get("/")
def home():
    return {"message": "RetailLens API running"}


@app.get("/events")
def get_events():
    return {"events": get_all_events()}


@app.get("/metrics")
def get_metrics():
    events = get_all_events()
    total = len(events)

    entries = sum(1 for e in events if e.get("event_type") == "ENTRY")
    exits = sum(1 for e in events if e.get("event_type") == "EXIT")

    return {
        "total_events": total,
        "entries": entries,
        "exits": exits
    }


@app.get("/funnel")
def get_funnel():
    events = get_all_events()

    entry = sum(1 for e in events if e.get("event_type") == "ENTRY")
    exit = sum(1 for e in events if e.get("event_type") == "EXIT")

    return {
        "entry": entry,
        "exit": exit,
        "conversion_rate": (exit / entry * 100) if entry > 0 else 0
    }

@app.post("/events/ingest")
def ingest_events(events: List[dict]):
    global event_store, event_ids

    added = 0
    duplicates = 0

    for event in events:
        event_id = event.get("event_id")

        if not event_id:
            continue

        if event_id in event_ids:
            duplicates += 1
            continue

        event_store.append(event)
        event_ids.add(event_id)
        added += 1

    return {
        "message": "Processed",
        "added": added,
        "duplicates": duplicates,
        "total_events": len(event_store)
    }

@app.post("/add-event")
def add_event(event: Event):
    new_event = {
        "event_id": str(uuid.uuid4()),
        "store_id": event.store_id,
        "camera_id": event.camera_id,
        "visitor_id": event.visitor_id,
        "event_type": event.event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "zone_id": None,
        "dwell_ms": 0,
        "is_staff": False,
        "confidence": 0.9,
        "metadata": {
            "queue_depth": None,
            "sku_zone": None,
            "session_seq": 0
        }
    }

    event_store.append(new_event)

    return {"message": "Event added successfully", "event": new_event}

@app.get("/stores/{store_id}/metrics")
def store_metrics(store_id: str):
    events = get_all_events()

    store_events = [e for e in events if e.get("store_id") == store_id]

    unique_visitors = len(set(e.get("visitor_id") for e in store_events))
    entries = sum(1 for e in store_events if e.get("event_type") == "ENTRY")
    exits = sum(1 for e in store_events if e.get("event_type") == "EXIT")

    return {
        "store_id": store_id,
        "unique_visitors": unique_visitors,
        "entries": entries,
        "exits": exits,
        "conversion_rate": (exits / entries * 100) if entries > 0 else 0
    }

@app.get("/stores/{store_id}/funnel")
def store_funnel(store_id: str):
    events = get_all_events()

    # Filter events for this store
    store_events = [e for e in events if e.get("store_id") == store_id]

    # Unique visitors who entered
    entered_visitors = set(
        e["visitor_id"] for e in store_events if e["event_type"] == "ENTRY"
    )

    # Unique visitors who exited
    exited_visitors = set(
        e["visitor_id"] for e in store_events if e["event_type"] == "EXIT"
    )

    # Converted = visitors who both entered AND exited
    converted = entered_visitors.intersection(exited_visitors)

    return {
        "store_id": store_id,
        "entry": len(entered_visitors),
        "exit": len(converted),
        "conversion_rate": (len(converted) / len(entered_visitors) * 100)
        if entered_visitors else 0
    }

@app.get("/stores/{store_id}/heatmap")
def get_heatmap(store_id: str):
    events = get_all_events()

    # Filter store events
    store_events = [e for e in events if e.get("store_id") == store_id]

    zone_data = {}

    for e in store_events:
        zone = e.get("zone_id")
        if not zone:
            continue

        if zone not in zone_data:
            zone_data[zone] = {
                "visits": 0,
                "total_dwell": 0
            }

        # Count zone enter
        if e.get("event_type") == "ZONE_ENTER":
            zone_data[zone]["visits"] += 1

        # Add dwell time
        if e.get("event_type") == "ZONE_DWELL":
            zone_data[zone]["total_dwell"] += e.get("dwell_ms", 0)

    # Compute avg dwell + normalize
    result = []
    max_visits = max([z["visits"] for z in zone_data.values()], default=1)

    for zone, data in zone_data.items():
        avg_dwell = data["total_dwell"] / data["visits"] if data["visits"] > 0 else 0

        normalized = int((data["visits"] / max_visits) * 100)

        result.append({
            "zone_id": zone,
            "visits": data["visits"],
            "avg_dwell_ms": avg_dwell,
            "heat_score": normalized
        })

    return {
        "store_id": store_id,
        "zones": result,
	"data_confidence": "LOW" if len(store_events) < 20 else "HIGH"
    }

@app.get("/stores/{store_id}/anomalies")
def get_anomalies(store_id: str):
    events = get_all_events()

    store_events = [e for e in events if e.get("store_id") == store_id]

    anomalies = []

    # ---------- 1. DEAD ZONE ----------
    zones_visited = set(
        e.get("zone_id") for e in store_events if e.get("zone_id")
    )

    all_possible_zones = {"COSMETICS", "SKINCARE", "BILLING"}

    dead_zones = all_possible_zones - zones_visited

    for zone in dead_zones:
        anomalies.append({
            "type": "DEAD_ZONE",
            "severity": "WARN",
            "zone": zone,
            "message": f"No activity in {zone}",
            "suggested_action": "Check product placement or visibility"
        })

    # ---------- 2. ENTRY-EXIT IMBALANCE ----------
    entry = sum(1 for e in store_events if e.get("event_type") == "ENTRY")
    exit = sum(1 for e in store_events if e.get("event_type") == "EXIT")

    if entry > 5 and exit < entry * 0.5:
        anomalies.append({
            "type": "LOW_EXIT_RATE",
            "severity": "HIGH",
            "message": "High entries but low exits",
            "suggested_action": "Possible crowd buildup or stuck customers"
        })

    # ---------- 3. NO EXIT ----------
    if entry > 3 and exit == 0:
        anomalies.append({
            "type": "NO_EXIT",
            "severity": "HIGH",
            "message": "No exits detected",
            "suggested_action": "Check exit cameras or congestion"
        })

    # ---------- 4. TRAFFIC SPIKE ----------
    if entry > 10:
        anomalies.append({
            "type": "HIGH_TRAFFIC",
            "severity": "INFO",
            "message": "Unusually high store traffic",
            "suggested_action": "Deploy more staff if needed"
        })

    return {
        "store_id": store_id,
        "total_events": len(store_events),
        "entry": entry,
        "exit": exit,
        "anomalies": anomalies
    }