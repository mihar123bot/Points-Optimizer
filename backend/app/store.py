from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TRIP_SEARCHES_FILE = DATA_DIR / "trip_searches.json"
ALERTS_FILE = DATA_DIR / "alerts.json"
RECOMMENDATIONS_FILE = DATA_DIR / "recommendations.json"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def load_trip_searches() -> dict[str, Any]:
    return _load(TRIP_SEARCHES_FILE)


def save_trip_searches(data: dict[str, Any]) -> None:
    _save(TRIP_SEARCHES_FILE, data)


def load_alerts() -> dict[str, Any]:
    return _load(ALERTS_FILE)


def save_alerts(data: dict[str, Any]) -> None:
    _save(ALERTS_FILE, data)


def load_recommendations() -> dict[str, Any]:
    return _load(RECOMMENDATIONS_FILE)


def save_recommendations(data: dict[str, Any]) -> None:
    _save(RECOMMENDATIONS_FILE, data)
