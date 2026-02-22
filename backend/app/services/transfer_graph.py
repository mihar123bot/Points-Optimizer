"""
Transfer graph — in-memory, built once at import from transfer_partners.py CSV data.
Models the PRD §8 transfer_edges table without a database.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from app.data.transfer_partners import PROGRAMS

# ── Card column → backend currency key ───────────────────────────────────────
_COL_TO_CURRENCY: dict[str, str] = {
    "amex":         "MR",
    "chase":        "CHASE",
    "capital_one":  "CAP1",
    "citi":         "CITI",
    "bilt":         "BILT",
    "wells_fargo":  "WF",
}

# ── Known slow transfer times (minutes) ──────────────────────────────────────
# Overrides for programs that take longer than instant.
_TRANSFER_TIME_OVERRIDES: dict[tuple[str, str], int] = {
    ("MR",    "Singapore KrisFlyer"):       2880,   # 2 days
    ("MR",    "ANA Mileage Club"):          4320,   # 3 days
    ("CAP1",  "Singapore KrisFlyer"):       2880,   # 2 days
    ("MR",    "Avianca LifeMiles"):            0,   # instant
    ("CAP1",  "Avianca LifeMiles"):            0,   # instant
    ("MR",    "Flying Blue"):                  0,   # instant
    ("MR",    "British Airways Avios"):        0,   # instant
    ("MR",    "Virgin Atlantic Flying Club"):  0,   # instant
    ("MR",    "Delta SkyMiles"):               0,   # instant
    ("CAP1",  "Air Canada Aeroplan"):          0,   # instant
    ("CAP1",  "Turkish Miles&Smiles"):         0,   # instant
    ("CAP1",  "British Airways Avios"):        0,   # instant
    ("BILT",  "Air Canada Aeroplan"):          0,   # instant
    ("BILT",  "Flying Blue"):                  0,   # instant
    ("BILT",  "British Airways Avios"):        0,   # instant
    ("BILT",  "American AAdvantage"):          0,   # instant
    ("BILT",  "United MileagePlus"):           0,   # instant
    ("CITI",  "Flying Blue"):                  0,   # instant
    ("CITI",  "Turkish Miles&Smiles"):         0,   # instant
    ("CITI",  "Avianca LifeMiles"):            0,   # instant
    ("WF",    "Flying Blue"):                  0,   # instant
    ("WF",    "British Airways Avios"):        0,   # instant
}

_DEFAULT_TRANSFER_TIME = 1440  # 1 day if unknown


@dataclass(frozen=True)
class TransferEdge:
    currency: str               # "MR", "CAP1", etc.
    program: str                # "Air Canada Aeroplan"
    airline: str                # "Air Canada"
    alliance: str               # "Star Alliance"
    ratio: float = 1.0          # transfer ratio (1.0 = 1:1)
    promo_bonus_percent: float = 0.0
    transfer_time_minutes: int = 0


# ── Build edge list at import time ────────────────────────────────────────────
TRANSFER_EDGES: list[TransferEdge] = []
for _prog in PROGRAMS:
    for _col, _currency in _COL_TO_CURRENCY.items():
        if _prog.get(_col) == 1:
            _key = (_currency, _prog["program"])
            TRANSFER_EDGES.append(TransferEdge(
                currency=_currency,
                program=_prog["program"],
                airline=_prog["airline"],
                alliance=_prog["alliance"],
                ratio=1.0,   # all known transfers are 1:1 in the current table
                promo_bonus_percent=0.0,
                transfer_time_minutes=_TRANSFER_TIME_OVERRIDES.get(_key, _DEFAULT_TRANSFER_TIME),
            ))


def get_edges_for_currency(currency: str) -> list[TransferEdge]:
    """All programs reachable from a given currency key (e.g. 'MR')."""
    return [e for e in TRANSFER_EDGES if e.currency == currency]


def get_edges_for_airline(airline_name: str) -> list[TransferEdge]:
    """
    All edges whose program flies the given airline (case-insensitive partial match
    on the airline field from the PROGRAMS table).
    """
    key = airline_name.lower()
    return [e for e in TRANSFER_EDGES if key in e.airline.lower()]


def build_transfer_paths(
    airline: str,
    user_balances: dict[str, int],
    points_needed: int,
) -> list[dict]:
    """
    Build structured transfer paths for the PRD §8/§9 output shape.

    Returns a list of dicts compatible with the TransferPath Pydantic model,
    sorted: viable paths (effective_points >= needed) first, then by transfer speed.

    Args:
        airline: Operating airline name (e.g. "Air France")
        user_balances: {"MR": 80000, "CAP1": 50000, ...}
        points_needed: Award points required for this itinerary
    """
    candidate_edges = get_edges_for_airline(airline)
    paths: list[dict] = []
    seen: set[tuple[str, str]] = set()  # (currency, program) dedup

    for edge in candidate_edges:
        balance = user_balances.get(edge.currency, 0)
        if balance <= 0:
            continue
        key = (edge.currency, edge.program)
        if key in seen:
            continue
        seen.add(key)

        effective = int(balance * edge.ratio * (1 + edge.promo_bonus_percent / 100))
        paths.append({
            "currency": edge.currency,
            "program": edge.program,
            "ratio": edge.ratio,
            "promo_bonus_percent": edge.promo_bonus_percent,
            "effective_points": effective,
            "transfer_time_minutes": edge.transfer_time_minutes,
        })

    # Sort: viable first, then fastest transfer
    def _sort_key(p: dict) -> tuple:
        viable = p["effective_points"] >= points_needed
        return (not viable, p["transfer_time_minutes"])

    return sorted(paths, key=_sort_key)
