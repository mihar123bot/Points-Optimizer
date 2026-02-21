# PointsTrip Optimizer (MVP)

Semi-auto credit card points trip optimizer.

## What you get now
- FastAPI backend for Trip Search, Recommendations, Playbook, Alerts
- Streamlit app UI as the output interface
- Persistent local JSON storage for trip searches + alerts
- Transparent OOP/CPP/friction scoring scaffold

## Quick start

```bash
cd Points-Optimizer
./run.sh
```

- Backend API: `http://localhost:8000/docs`
- Streamlit App: `http://localhost:8502`

## Manual run (optional)

Backend:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend app:
```bash
cd ..
pip install -r requirements.txt
streamlit run app.py --server.port 8502
```

## Project Layout
- `app.py` — Streamlit app (main UI)
- `backend/` — API + services + models + store
- `docs/` — architecture, API contract, build tasklist

## Next build targets
- Real provider adapters (award + airfare + hotel)
- Marriott CPP rule enforcement in hotel results
- Saved-search alert evaluator jobs
