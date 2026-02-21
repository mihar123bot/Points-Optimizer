# PointPilot

Fly smarter with points you already have.

PointPilot is a points-first trip planning app that helps you:
- search trips,
- compare ranked options,
- generate a booking playbook.

No auto-booking is performed.

---

## Current App Status

### Primary UI (default)
- **Next.js + TypeScript frontend** in `frontend/`
- **Desktop/web-first layout** (mobile styling still supported)
- Roame-inspired cinematic hero + structured search tray
- 3-step flow:
  1. Search
  2. Options
  3. Playbook
- Simple / Nerd mode toggle

### Backend
- FastAPI backend in `backend/`
- Endpoints for trip search, recommendations, and playbook generation
- Local JSON persistence for MVP

### Legacy UI
- Streamlit app (`app.py`) still exists for internal fallback/testing
- Not the default UI anymore

---

## Architecture

### Frontend (default)
- `frontend/app/page.tsx` (main UI flow)
- `frontend/app/globals.css` (visual system)
- `frontend/lib/api.ts` (API calls)
- `frontend/lib/types.ts` (TS models)

### Backend
- `backend/app/main.py`
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

---

## MVP Scope Constraints

### Origins
- US departures only (enforced)

### Destination allowlist
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

Current destination pool codes include:
`CUN, PUJ, NAS, SJD, YVR, EZE, LIM, CDG, FCO, LHR, KEF, ATH, HND, BKK`

---

## Setup

## 1) Install dependencies

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend (default)
```bash
cd ../frontend
npm install
```

---

## 2) Environment variables

### Backend env (`backend/.env`)

```bash
AMADEUS_CLIENT_ID=your_id
AMADEUS_CLIENT_SECRET=your_secret
SEATS_AERO_API_KEY=your_key_optional
SEATS_AERO_URL=https://your-award-endpoint.example.com/search
```

### Frontend env (`frontend/.env.local`)

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

---

## 3) Run services

### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend (default)
```bash
cd frontend
npm run dev
```

Open:
- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

---

## API Endpoints (MVP)

- `GET /health`
- `POST /v1/trip-searches`
- `GET /v1/trip-searches/{id}`
- `POST /v1/recommendations/generate`
- `POST /v1/playbook/generate`
- `POST /v1/alerts`
- `GET /v1/alerts`
- `PATCH /v1/alerts/{id}`

---

## Notes

- Recommendations use a short in-memory cache (TTL-based) for repeated identical requests.
- Live/fallback behavior is transparent in API response fields (`api_mode`, source labels/timestamps).
- Local JSON storage is fine for MVP/demo but not production scale.
