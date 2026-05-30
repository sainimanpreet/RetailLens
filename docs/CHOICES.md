# Design Choices

## 1. YOLOv8 for Detection
YOLOv8 was chosen because:
- It provides high accuracy
- Works well in real-time scenarios
- Easy integration using Ultralytics API

---

## 2. Line Crossing Logic
Instead of complex behavior models:
- A simple horizontal line is used
- Crossing direction determines ENTRY or EXIT
- This reduces computation cost and complexity

---

## 3. JSONL Storage Format
JSONL (JSON Lines) was chosen because:
- Efficient for streaming large data
- Easy to append events
- Works well with real-time systems

---

## 4. FastAPI Backend
FastAPI was selected because:
- High performance
- Easy API development
- Built-in documentation support

---

## 5. Modular Architecture
Code is separated into:
- pipeline/
- app/
- tests/
- docs/

This improves scalability and maintainability.

# 🧠 CHOICES.md — Key Design Decisions

This document explains important design decisions made during the development of the **RetailLens System**, including alternatives considered and final justifications.

---

## 6. Event Ingestion Strategy — Single Event API vs Batch Processing

### Options considered

* **Single Event API (POST /add-event)**

  * Simple implementation
  * Easy debugging
  * Low latency per request

* **Batch Ingestion (POST /events/ingest)**

  * Efficient for large event streams
  * Reduces API overhead
  * Closer to real-world pipelines

---

### What AI initially suggested

The initial approach focused on a simple single-event API (`POST /add-event`) for easier implementation.

---

### What we chose and why

We implemented **both approaches**:

* `POST /add-event` → for testing & manual usage
* `POST /events/ingest` → for scalable ingestion

This provides:

* Flexibility for testing
* Scalability for real-time pipelines

---

### Trade-offs accepted

* Slight increase in API complexity
* Additional validation logic required

---

## 7. Event Schema Design — Minimal vs Extensible Schema

### Options considered

* **Minimal schema**

  ```json
  { "event_type": "ENTRY" }
  ```

  * Easy to implement
  * Not scalable

* **Structured schema (chosen)**

  ```json
  {
    "store_id": "STORE_001",
    "camera_id": "CAM_1",
    "visitor_id": "V101",
    "event_type": "ENTRY"
    }
  ```

  * More informative
  * Supports analytics
  * Extensible

  ---

  ### What AI initially suggested

  A minimal schema with only `event_type` for simplicity.

  ---

  ### What we chose and why

  We designed a **structured event schema** because:

  * Analytics require context (store, visitor)
  * Enables future expansion (zones, timestamps)
  * Supports multiple endpoints (`/metrics`, `/funnel`)

  ---

  ### Trade-offs accepted

  * Slightly larger payload size
  * More validation required

  ---

  ## 8. Conversion Logic — Simple Count vs Funnel-Based Calculation

  ### Options considered

  * **Simple logic**

    ```
    conversion = exit / entry
    ```

    * Easy
    * Not realistic
  * **Funnel-based logic (chosen)**

    * ENTRY → EXIT → conversion
    * Can extend to:

      * ZONE visits
      * Billing events

  ---

  ### What AI initially suggested

  Basic division-based conversion calculation.

  ---

  ### What we chose and why

  We implemented funnel-style logic:

  * Tracks customer journey
  * More aligned with real retail analytics
  * Easily extendable

  ---

  ### Trade-offs accepted

  * Slightly more computation
  * Requires clean event data

  ---

  ## 9. Storage Strategy — In-Memory vs Database

  ### Options considered

  * **In-memory storage (chosen)**

    * Fast
    * Simple
    * No setup required
  * **Database (PostgreSQL / SQLite)**

    * Persistent
    * Scalable
    * More complex setup

  ---

  ### What AI initially suggested

  Using a full database for production-level design.

  ---

  ### What we chose and why

  We used **in-memory storage** because:

  * Faster development
  * Suitable for assignment/demo
  * No external dependencies

  ---

  ### Trade-offs accepted

  * Data is lost on restart
  * Not production-ready

  ---

  ##  Deployment Strategy — Local vs Docker

  ### Options considered

  * **Local run**

    ```
    uvicorn app.main:app
    ```

    * Simple
    * Not portable
  * **Docker deployment (chosen)**

    * Portable
    * Reproducible
    * Industry standard

  ---

  ### What AI initially suggested

  Running locally using Uvicorn.

  ---

  ### What we chose and why

  We used **Docker** because:

  * Ensures environment consistency
  * Easy to deploy anywhere
  * Required by assignment

  ---

  ### Trade-offs accepted

  * Slightly longer setup time
  * Requires Docker installation

  ---

  ## 10. API Design — REST vs Complex Architecture

  ### Options considered

  * **Simple REST APIs (chosen)**

    * Easy to understand
    * Fast to implement
  * **Microservices / streaming architecture**

    * Scalable
    * Overkill for this use case

  ---

  ### What AI initially suggested

  More complex distributed architecture.

  ---

  ### What we chose and why

  We used **simple REST APIs**:

  * `/metrics`
  * `/funnel`
  * `/events`
  * `/health`

  This keeps:

  * System simple
  * Easy to test
  * Easy to deploy

  ---

  ### Trade-offs accepted

  * Limited scalability
  * Not distributed

  ---

  ## ✅ Summary

  The system balances:

  * Simplicity
  * Performance
  * Practical implementation

  Key focus:

  * Clean API design
  * Real-time analytics
  * Docker-based deployment

  ---

