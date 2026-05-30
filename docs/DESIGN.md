# 🏬 RetailLens System — Design

---

## 1. Problem

Retail stores need insights like:

* How many customers entered?
* How many converted (purchased)?
* Where do customers spend time?

Raw CCTV footage is unstructured.
This system converts video-generated events into **real-time analytics** using a containerized backend.

---

## 2. Architecture

```
CCTV / Simulator
        ↓
Event Generator (pipeline)
        ↓
POST /events/ingest
        ↓
FastAPI Backend (app/)
        ↓
In-Memory / DB Storage
        ↓
Analytics APIs
   ├── /metrics
   ├── /funnel
   ├── /events
   └── /health
```

---

## 3. Data Flow

1. Events are generated using:

   * `pipeline/detect.py` OR `simulator.py`

2. Each event contains:

   * store_id
   * visitor_id
   * event_type (ENTRY, EXIT, etc.)

3. Events are sent to:

   ```
   POST /events/ingest
   ```

4. Backend:

   * Validates using Pydantic schema
   * Stores events
   * Deduplicates if needed

5. APIs compute real-time insights:

   * `/metrics` → visitor count
   * `/funnel` → conversion rate

---

## 4. Event Schema Design

```json
{
  "store_id": "STORE_001",
  "camera_id": "CAM_1",
  "visitor_id": "V101",
  "event_type": "ENTRY"
}
```

### Design Decisions:

* Single flexible schema
* Supports multiple event types
* Easy to extend

---

## 5. Storage & Idempotency

* Events stored in structured format
* Duplicate events avoided using:

  * unique visitor_id + event logic

Why this matters:

* Prevents double counting
* Ensures accurate metrics

---

## 6. Observability

* FastAPI logs each request

* Health endpoint:

  ```
  GET /health
  ```

* Helps check:

  * API status
  * system health

---

## 7. Error Handling

* Validation errors → 422
* Server errors → 500
* Clean JSON responses

Example:

```json
{
  "error": "Invalid event data"
}
```

---

## 8. Deployment (Docker)

The system is containerized using Docker.

### Components:

* FastAPI backend
* Docker container runtime

### Run:

```bash
docker compose up --build
```

### Access:

```
http://localhost:8000/docs
```

---

## 9. Testing Strategy

* API tested using Swagger UI
* Manual event testing:

  * POST /add-event
* Real-time validation via metrics endpoints

---

## 10. AI-Assisted Decisions

AI tools helped in:

* API structuring
* Schema validation
* Debugging Docker issues

Manual decisions:

* Simplified event schema
* Lightweight architecture (no heavy DB dependency)

---

## 11. Out of Scope

* Multi-store scaling
* Authentication system
* Advanced ML models (YOLO full pipeline)

---

## ✅ Summary

This system converts raw event streams into:

* Real-time insights
* Scalable API endpoints
* Dockerized deployment

Designed for:

* Simplicity
* Performance
* Easy deployment
