from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class AwardProvider:
    def search(self, origin: str, destination: str, travelers: int) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        # Placeholder for live adapter hookup.
        return {
            "points_cost": 38000 + (hash(destination) % 12000),
            "taxes_fees": 120 + (hash(origin + destination) % 80),
            "program": "MR",
            "as_of": now,
            "source": "award_adapter_mock",
        }


class AirfareProvider:
    def search(self, origin: str, destination: str, travelers: int) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        base = 380 + (hash(destination) % 220)
        return {
            "cash_price_total": float(base * max(travelers, 1)),
            "as_of": now,
            "source": "airfare_adapter_mock",
        }


class HotelProvider:
    def search(self, destination: str, nights: int, travelers: int) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        cash_rate = float((140 + (hash(destination) % 120)) * max(nights, 1))
        points_rate = int((32000 + (hash(destination + 'hotel') % 30000)) * max(nights / 5, 0.6))
        fees = float(35 + (hash(destination) % 40))
        return {
            "cash_rate_all_in": cash_rate,
            "points_rate": points_rate,
            "fees_on_points": fees,
            "as_of": now,
            "source": "hotel_adapter_mock",
        }
