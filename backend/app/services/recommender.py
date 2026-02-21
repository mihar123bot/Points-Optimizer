from __future__ import annotations

from typing import Any


# MVP rollout scope requested by user:
# North America, Argentina, Peru, France, Italy, UK, Iceland, Greece, Japan, Thailand
DESTINATION_POOL = [
    # North America / Caribbean
    {"code": "CUN", "city": "Cancun", "region": "north america warm beach", "travel_hours": 4.3, "stops": 0},
    {"code": "PUJ", "city": "Punta Cana", "region": "north america warm beach", "travel_hours": 4.8, "stops": 0},
    {"code": "NAS", "city": "Nassau", "region": "north america warm beach", "travel_hours": 3.1, "stops": 0},
    {"code": "SJD", "city": "Los Cabos", "region": "north america warm beach", "travel_hours": 6.1, "stops": 1},
    {"code": "YVR", "city": "Vancouver", "region": "north america", "travel_hours": 6.0, "stops": 0},
    # South America
    {"code": "EZE", "city": "Buenos Aires", "region": "argentina south america", "travel_hours": 10.0, "stops": 1},
    {"code": "LIM", "city": "Lima", "region": "peru south america warm beach", "travel_hours": 7.8, "stops": 1},
    # Europe
    {"code": "CDG", "city": "Paris", "region": "france europe", "travel_hours": 7.8, "stops": 0},
    {"code": "FCO", "city": "Rome", "region": "italy europe", "travel_hours": 8.7, "stops": 0},
    {"code": "LHR", "city": "London", "region": "uk europe", "travel_hours": 7.2, "stops": 0},
    {"code": "KEF", "city": "Reykjavik", "region": "iceland europe", "travel_hours": 5.9, "stops": 0},
    {"code": "ATH", "city": "Athens", "region": "greece europe warm beach", "travel_hours": 9.8, "stops": 1},
    # Asia
    {"code": "HND", "city": "Tokyo", "region": "japan asia", "travel_hours": 13.5, "stops": 1},
    {"code": "BKK", "city": "Bangkok", "region": "thailand asia warm beach", "travel_hours": 18.0, "stops": 1},
]


def generate_destination_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    constraints = payload.get("constraints", {})
    max_hours = float(constraints.get("max_travel_hours", 10.0))
    max_stops = int(constraints.get("max_stops", 1))
    vibe_tags = [v.lower().strip() for v in payload.get("vibe_tags", []) if str(v).strip()]
    preferred = [d.lower().strip() for d in payload.get("preferred_destinations", []) if str(d).strip()]

    wants_beach_warm = any(v in {"beach", "warm", "warm beach"} for v in vibe_tags)

    out: list[dict[str, Any]] = []
    for d in DESTINATION_POOL:
        if d["travel_hours"] > max_hours or d["stops"] > max_stops:
            continue

        # Beach/warm should not drift to off-vibe defaults.
        if wants_beach_warm and not ("beach" in d["region"] or "warm" in d["region"]):
            continue

        if vibe_tags and not wants_beach_warm and not any(v in d["region"] for v in vibe_tags):
            continue

        if preferred:
            code = d["code"].lower()
            city = d["city"].lower()
            if not any((p == code) or (p in city) for p in preferred):
                continue

        out.append(d)

    return out[:10]
