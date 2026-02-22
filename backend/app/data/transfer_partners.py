"""
Transfer partners table: which credit card programs can transfer to which
airline loyalty programs.

Source: backend/data/transfer_partners.csv
"""
from __future__ import annotations

# ── Card column → backend program key ────────────────────────────────────────
# Maps CSV column names to the program keys used throughout the engine.
CARD_TO_BACKEND: dict[str, str] = {
    "amex": "MR",
    "chase": "CHASE",
    "capital_one": "CAP1",
    "citi": "CITI",
    "bilt": "BILT",
    "wells_fargo": "WF",
}

CARD_COLUMNS: list[str] = list(CARD_TO_BACKEND.keys())

# ── Full program table ────────────────────────────────────────────────────────
# Each dict mirrors one row of transfer_partners.csv.
PROGRAMS: list[dict] = [
    {"program": "Aeromexico Rewards",         "airline": "Aeromexico",       "alliance": "SkyTeam",      "amex": 1, "chase": 0, "capital_one": 1, "citi": 1, "bilt": 0, "wells_fargo": 0},
    {"program": "Air Canada Aeroplan",         "airline": "Air Canada",       "alliance": "Star Alliance", "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 0},
    {"program": "Flying Blue",                 "airline": "Air France/KLM",   "alliance": "SkyTeam",      "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 1},
    {"program": "Alaska Mileage Plan",         "airline": "Alaska",           "alliance": "Oneworld",     "amex": 0, "chase": 0, "capital_one": 0, "citi": 0, "bilt": 1, "wells_fargo": 0},
    {"program": "American AAdvantage",         "airline": "American",         "alliance": "Oneworld",     "amex": 0, "chase": 0, "capital_one": 0, "citi": 0, "bilt": 1, "wells_fargo": 1},
    {"program": "Avianca LifeMiles",           "airline": "Avianca",          "alliance": "Star Alliance", "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 0},
    {"program": "British Airways Avios",       "airline": "British Airways",  "alliance": "Oneworld",     "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 1},
    {"program": "Cathay Pacific Asia Miles",   "airline": "Cathay Pacific",   "alliance": "Oneworld",     "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 0},
    {"program": "Copa ConnectMiles",           "airline": "Copa",             "alliance": "Star Alliance", "amex": 0, "chase": 0, "capital_one": 1, "citi": 1, "bilt": 0, "wells_fargo": 0},
    {"program": "Delta SkyMiles",              "airline": "Delta",            "alliance": "SkyTeam",      "amex": 1, "chase": 0, "capital_one": 0, "citi": 0, "bilt": 0, "wells_fargo": 0},
    {"program": "Emirates Skywards",           "airline": "Emirates",         "alliance": "None",         "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 1},
    {"program": "Etihad Guest",                "airline": "Etihad",           "alliance": "None",         "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 0},
    {"program": "Finnair Plus",                "airline": "Finnair",          "alliance": "Oneworld",     "amex": 0, "chase": 0, "capital_one": 1, "citi": 0, "bilt": 0, "wells_fargo": 0},
    {"program": "Iberia Avios",                "airline": "Iberia",           "alliance": "Oneworld",     "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 1},
    {"program": "JetBlue TrueBlue",            "airline": "JetBlue",          "alliance": "None",         "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 1},
    {"program": "Lufthansa Miles & More",      "airline": "Lufthansa",        "alliance": "Star Alliance", "amex": 0, "chase": 0, "capital_one": 0, "citi": 0, "bilt": 1, "wells_fargo": 0},
    {"program": "Qantas Frequent Flyer",       "airline": "Qantas",           "alliance": "Oneworld",     "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 1},
    {"program": "Qatar Airways Avios",         "airline": "Qatar",            "alliance": "Oneworld",     "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 1},
    {"program": "SAS EuroBonus",               "airline": "SAS",              "alliance": "Star Alliance", "amex": 1, "chase": 0, "capital_one": 1, "citi": 1, "bilt": 0, "wells_fargo": 0},
    {"program": "Singapore KrisFlyer",         "airline": "Singapore Airlines","alliance": "Star Alliance", "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 1},
    {"program": "Turkish Miles&Smiles",        "airline": "Turkish Airlines", "alliance": "Star Alliance", "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 0},
    {"program": "United MileagePlus",          "airline": "United",           "alliance": "Star Alliance", "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 0},
    {"program": "Virgin Atlantic Flying Club", "airline": "Virgin Atlantic",  "alliance": "None",         "amex": 1, "chase": 1, "capital_one": 1, "citi": 1, "bilt": 1, "wells_fargo": 1},
    {"program": "Virgin Australia Velocity",   "airline": "Virgin Australia", "alliance": "None",         "amex": 1, "chase": 0, "capital_one": 1, "citi": 1, "bilt": 0, "wells_fargo": 0},
]

# ── Index by airline name for quick lookup ────────────────────────────────────
_AIRLINE_INDEX: dict[str, list[dict]] = {}
for _p in PROGRAMS:
    _key = _p["airline"].lower()
    _AIRLINE_INDEX.setdefault(_key, []).append(_p)


def get_transferable_programs(card: str) -> list[dict]:
    """Return all programs transferable from *card* (use CSV column name, e.g. 'amex')."""
    col = card.lower()
    if col not in CARD_COLUMNS:
        return []
    return [p for p in PROGRAMS if p.get(col) == 1]


def get_cards_for_program(program_name: str) -> list[str]:
    """Return CSV column names of cards that can transfer to *program_name*."""
    for p in PROGRAMS:
        if p["program"].lower() == program_name.lower():
            return [col for col in CARD_COLUMNS if p.get(col) == 1]
    return []


def get_programs_for_airline(airline: str) -> list[dict]:
    """Return programs whose airline matches *airline* (case-insensitive, partial ok)."""
    key = airline.lower()
    # Try exact key first, then partial match
    if key in _AIRLINE_INDEX:
        return _AIRLINE_INDEX[key]
    return [p for p in PROGRAMS if key in p["airline"].lower()]


def get_transferable_programs_for_backend(backend_key: str) -> list[dict]:
    """
    Given an engine-backend key (e.g. 'MR', 'CAP1'), return all programs
    reachable from that issuer's card.
    """
    # Reverse-map backend key → CSV column
    col = next((c for c, k in CARD_TO_BACKEND.items() if k == backend_key), None)
    if col is None:
        return []
    return get_transferable_programs(col)
