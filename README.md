# PointsTrip Optimizer (MVP)

Semi-automated points trip optimizer for early rollout (friends/family).

This app helps a user:
- search trip options,
- compare out-of-pocket (OOP) vs points value,
- generate a booking playbook (transfer + booking steps),
- export that playbook.

No auto-booking is performed.

---

## Current MVP Status (as of latest commit)

### Implemented
- FastAPI backend with endpoints for:
  - Trip Search
  - Recommendations generation
  - Booking Playbook generation
  - Alerts CRUD (basic)
- Streamlit app with a decision-first UI:
  - Step 1: Search Trips
  - Step 2: Decision View (top 3 options)
  - Advanced Details (compare + transparency)
- Optional destination hint input (`To destination (optional)`)
- Dynamic playbook logic (no longer static template)
- Option compare mode (up to 3 options)
- Booking plan export (`.md`)
- Transparent scoring payload per option:
  - points breakdown
  - friction components
  - score components
  - source timestamps/labels
- Marriott hotel points threshold enforcement:
  - points hotel mode only when hotel CPP >= 1.5¢/pt
  - otherwise hotel defaults to cash mode for that option
- API mode status in UI:
  - `LIVE` when real provider data is used
  - `FALLBACK` when estimator/mock data is used

### Data/provider mode
- **Cash flights:** Free-tier Amadeus test API path implemented (if keys provided)
- **Hotels:** Free-tier Amadeus test API path implemented (if keys provided)
- **Award points availability:** MVP estimator fallback (real free award API is limited/gated)
- If Amadeus credentials are missing or API call fails, app gracefully falls back to mock/estimator paths.

---

## Scope Constraints (MVP rollout)

### Origins
- US departures only (enforced in backend recommendations route)

### Destination coverage (allowlisted)
- North America
- Argentina
- Peru
- France
- Italy
- UK
- Iceland
- Greece
- Japan
- Thailand

Current destination pool codes include: `CUN, PUJ, NAS, SJD, YVR, EZE, LIM, CDG, FCO, LHR, KEF, ATH, HND, BKK`

---

## Architecture

### Frontend
- `app.py` (Streamlit)
- Google Flights-inspired input layout:
  - row 1: Trip type, Travelers, Cabin, Nights
  - row 2: From + To destination (optional)
  - row 3: Depart/Return + Search CTA
  - row 4: Reward Points Optimization inputs

### Backend
- FastAPI app (`backend/app/main.py`)
- Routers:
  - `trip_searches.py`
  - `recommendations.py`
  - `playbook.py`
  - `alerts.py`
- Services:
  - `recommender.py`
  - `scoring.py`
- Adapters:
  - `adapters/providers.py`

### Persistence (local JSON)
- `backend/data/trip_searches.json`
- `backend/data/recommendations.json`
- `backend/data/alerts.json`

---

## API/Scoring Behavior

### Recommendations pipeline
1. Validate trip search + origin constraints
2. Generate destination candidates from allowlist + constraints + optional preferred destination hints
3. Pull provider data (or fallback):
   - airfare cash,
   - hotel cash/points estimate,
   - award estimate
4. Compute metrics:
   - OOP
   - flight CPP
   - hotel CPP
   - blended CPP (capped)
   - friction
   - composite score
5. Enforce Marriott hotel points rule (`CPP >= 1.5`)
6. Return winner tiles + ranked options

### Scoring model (MVP)
`score = w1 * (-OOP_norm) + w2 * CPP_norm + w3 * (-friction_norm)`
- default weights in code:
  - `w1 = 0.5`
  - `w2 = 0.35`
  - `w3 = 0.15`

### Explainability returned per option
- `points_breakdown`
- `friction_components`
- `score_components`
- `source_timestamps`
- `source_labels`
- `api_mode`

---

## Setup

## 1) Install dependencies

Backend deps:
```bash
cd backend
pip install -r requirements.txt
```

UI deps:
```bash
cd ..
pip install -r requirements.txt
```

## 2) Environment variables

Create env vars (or a `.env` in `backend/`) for live Amadeus path:

```bash
AMADEUS_CLIENT_ID=your_id
AMADEUS_CLIENT_SECRET=your_secret
```

Optional:
```bash
API_BASE=http://localhost:8000
```

Notes:
- Backend loads env via `python-dotenv` on startup.
- If Amadeus vars are absent, app still runs in fallback mode.

## 3) Run services

Backend:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

App:
```bash
cd ..
streamlit run app.py --server.port 8502
```

Open:
- API docs: `http://localhost:8000/docs`
- App: `http://localhost:8502`

---

## Endpoints (MVP)

- `GET /health`
- `POST /v1/trip-searches`
- `GET /v1/trip-searches/{id}`
- `POST /v1/recommendations/generate`
- `POST /v1/playbook/generate`
- `POST /v1/alerts`
- `GET /v1/alerts`
- `PATCH /v1/alerts/{id}`

---

## What is real vs placeholder right now

### Real-ish (production path started)
- Free-tier Amadeus calls for flights/hotels (when credentials available)
- Dynamic recommendation generation and ranking
- Dynamic booking playbook with warnings/fallbacks
- Export flow

### Placeholder / heuristic
- Award availability points pricing (estimator fallback)
- Some destination travel-time/stops assumptions in recommender pool
- Alerts delivery pipeline is not yet fully wired to email/push transport

---

## Known limitations

- Amadeus test environment has quota/coverage limitations
- Award inventory is not from a dedicated live award API yet
- Local JSON storage is fine for MVP but not multi-user production
- No auth/user accounts yet
- No booking automation by design

---

## Suggested next steps

1. Add one real award inventory provider adapter (if access approved)
2. Migrate storage from JSON to Postgres for reliability
3. Add caching layer (Redis) + provider retry/rate-limit controls
4. Add alert delivery channel (email first)
5. Add regression tests for scoring + playbook generation + origin/destination constraints

---

## Repo structure

```text
Points-Optimizer/
  app.py
  requirements.txt
  backend/
    requirements.txt
    .env.example
    app/
      main.py
      store.py
      domain/models.py
      routers/
        health.py
        trip_searches.py
        recommendations.py
        playbook.py
        alerts.py
      services/
        scoring.py
        recommender.py
      adapters/
        interfaces.py
        providers.py
    data/
      trip_searches.json
      recommendations.json
      alerts.json
  docs/
    ARCHITECTURE.md
    API_CONTRACT.md
    CODEX_TASKLIST.md
```
