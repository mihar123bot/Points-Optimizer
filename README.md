# PointPilot

**Explore. Discover. Capitalize.**

PointPilot is a points-first trip planning app. Enter your loyalty points balances, pick your dates, and get ranked award flight options with a step-by-step booking playbook — no auto-booking, full transparency.

---

## 3-Step Flow

| Step | What happens |
|------|-------------|
| **Explore** | Search by origin, destination, dates, cabin, and points balances |
| **Discover** | Ranked award options with OOP cost, CPP, and composite score |
| **Capitalize** | Booking playbook with transfer steps and booking instructions |

---

## Current Status

### Frontend
- **Next.js 14 + TypeScript** in `frontend/`
- Glassmorphic hero UI — blurred background, dark glass search panel
- Tagline and step breadcrumb reflect the 3-step Explore → Discover → Capitalize flow
- Search form embedded inside the hero glass card

### Search UI
- **Round trip / Travelers** — selectable in the top row
- Route row: From (multi-airport) + swap + To (optional, leave blank to explore all)
- Date row: Depart + Return
- Nights + Max travel hours
- **Points & Programs** — 3 collapsible program buckets (select program + enter balance)
  - Supported programs: Amex MR, Chase UR, Citi TYP, Capital One, Marriott Bonvoy, World of Hyatt
  - Balances are summed by backend type (MR / CAP1 / MARRIOTT) before submission

### Backend
- **FastAPI** in `backend/`
- Endpoints: trip search, recommendations, playbook
- Scoring: OOP (50%) + CPP (35%) + Friction (15%)
- Graceful degradation — live APIs (SeatsAero, Amadeus) with mock fallback
- Local JSON persistence (`data/*.json`) — MVP-grade

---

## Architecture

### Frontend
- `frontend/app/page.tsx` — full product UI (search, options, playbook steps)
- `frontend/app/globals.css` — glassmorphic design system
- `frontend/lib/api.ts` — API client
- `frontend/lib/types.ts` — TypeScript models

### Backend
- `backend/app/main.py` — FastAPI app + router setup
- Routers: `trip_searches.py`, `recommendations.py`, `playbook.py`, `alerts.py`
- Services: `recommender.py` (destination candidates), `scoring.py` (composite score)
- Adapters: `adapters/providers.py` (award, airfare, hotel providers)

---

## MVP Constraints

**Origins** — US airports:
`IAD, DCA, BWI, DFW, DAL, JFK, LGA, EWR, IAH, HOU, BOS, LAX, SFO, ORD, ATL, MIA, SEA`

**Destinations** — 14 destinations:
`CUN, PUJ, NAS, SJD, YVR, EZE, LIM, CDG, FCO, LHR, KEF, ATH, HND, BKK`

**Points programs** — MR (Amex/Chase/Citi), CAP1 (Capital One), MARRIOTT (Marriott/Hyatt)

---

## Setup

### 1. Install dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Environment variables

`backend/.env`:
```bash
AMADEUS_CLIENT_ID=your_id
AMADEUS_CLIENT_SECRET=your_secret
SEATS_AERO_API_KEY=your_key        # optional
SEATS_AERO_URL=https://...         # optional
```

`frontend/.env.local`:
```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### 3. Run locally

```bash
# Terminal 1 — backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

---

## Deploy

- Deploy `frontend/` to Vercel
- Set `NEXT_PUBLIC_API_BASE` in Vercel project env vars
- Host backend on Render / Railway / Fly.io

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/v1/trip-searches` | Create a trip search |
| `GET` | `/v1/trip-searches/{id}` | Get a trip search |
| `POST` | `/v1/recommendations/generate` | Generate ranked options |
| `POST` | `/v1/playbook/generate` | Generate booking playbook |
| `POST` | `/v1/alerts` | Create price alert |
| `GET` | `/v1/alerts` | List alerts |
| `PATCH` | `/v1/alerts/{id}` | Update alert |

---

## Notes

- Recommendations are short-TTL cached for repeated identical queries
- Every response includes `api_mode` (live vs fallback), source labels, and timestamps for transparency
- JSON persistence is MVP-grade — not production-scale
