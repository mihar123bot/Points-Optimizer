# PointsTrip Optimizer (MVP)

Semi-auto credit card points trip optimizer.

## MVP Goals
- Minimize out-of-pocket (OOP) for flight + hotel bundles
- Maximize realistic CPP using transparent math
- Generate a human-executable transfer + booking playbook (no auto-booking)

## Stack
- Backend: FastAPI
- Frontend: Next.js (placeholder scaffold in this repo)
- Data: Postgres (planned), Redis cache (planned)
- Jobs: scheduled refresh + alert checks

## Project Layout
- `docs/ARCHITECTURE.md` — system design and data flow
- `docs/API_CONTRACT.md` — MVP endpoints and payloads
- `docs/CODEX_TASKLIST.md` — build checklist and acceptance criteria
- `backend/` — FastAPI app + scoring + adapters
- `frontend/` — Next.js placeholder app shell

## Run (backend dev)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open API docs at: `http://localhost:8000/docs`

## Notes
- Provider adapters are intentionally interface-first for clean swap-in.
- Award/cash/hotel provider keys are env-based (`.env.example`).
- Includes transparent score explainability fields in responses.
