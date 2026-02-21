from __future__ import annotations

from typing import Any


DESTINATION_POOL = [
    {"code": "CUN", "region": "warm beach", "travel_hours": 4.3, "stops": 0},
    {"code": "PUJ", "region": "warm beach", "travel_hours": 4.8, "stops": 0},
    {"code": "NAS", "region": "warm beach", "travel_hours": 3.1, "stops": 0},
    {"code": "SDQ", "region": "warm beach", "travel_hours": 4.6, "stops": 1},
    {"code": "LIS", "region": "eastern europe beach", "travel_hours": 9.1, "stops": 1},
    {"code": "ATH", "region": "eastern europe beach", "travel_hours": 9.8, "stops": 1},
]


def generate_destination_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    constraints = payload.get("constraints", {})
    max_hours = float(constraints.get("max_travel_hours", 10.0))
    max_stops = int(constraints.get("max_stops", 1))
    vibe_tags = [v.lower() for v in payload.get("vibe_tags", [])]

    out: list[dict[str, Any]] = []
    for d in DESTINATION_POOL:
        if d["travel_hours"] > max_hours or d["stops"] > max_stops:
            continue
        if vibe_tags:
            if not any(v in d["region"] for v in vibe_tags):
                continue
        out.append(d)

    return out[:8]
