#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
cd "$ROOT"
pip install -q -r requirements.txt
streamlit run app.py --server.port 8502 --server.headless true
kill $API_PID || true
