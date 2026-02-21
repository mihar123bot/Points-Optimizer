from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import requests

AMADEUS_AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_FLIGHT_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"
AMADEUS_HOTEL_URL = "https://test.api.amadeus.com/v3/shopping/hotel-offers"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _amadeus_token() -> str | None:
    cid = os.getenv("AMADEUS_CLIENT_ID")
    csec = os.getenv("AMADEUS_CLIENT_SECRET")
    if not cid or not csec:
        return None
    try:
        r = requests.post(
            AMADEUS_AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": cid,
                "client_secret": csec,
            },
            timeout=12,
        )
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception:
        return None


class AwardProvider:
    """MVP fallback model for points cost when no free award API is available."""

    def search(self, origin: str, destination: str, travelers: int, cabin: str = "economy") -> dict[str, Any]:
        now = _now()
        # Real award APIs are typically paid/gated. Use conservative heuristic for MVP.
        base_cpp = 1.6 if cabin == "economy" else 2.0
        est_cash = 450 + (hash(origin + destination) % 250)
        taxes = float(95 + (hash(destination) % 70))
        points = int(max(12000, ((est_cash - taxes) / max(base_cpp, 0.8)) * 100))
        return {
            "points_cost": points,
            "taxes_fees": taxes,
            "program": "MR",
            "as_of": now,
            "source": "award_estimator_mvp",
        }


class AirfareProvider:
    def search(
        self,
        origin: str,
        destination: str,
        travelers: int,
        depart_date: str,
        return_date: str,
    ) -> dict[str, Any]:
        now = _now()
        token = _amadeus_token()
        if token:
            try:
                params = {
                    "originLocationCode": origin,
                    "destinationLocationCode": destination,
                    "departureDate": depart_date,
                    "adults": max(1, int(travelers)),
                    "currencyCode": "USD",
                    "max": 3,
                }
                if return_date and return_date != depart_date:
                    params["returnDate"] = return_date

                r = requests.get(
                    AMADEUS_FLIGHT_URL,
                    params=params,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=15,
                )
                r.raise_for_status()
                data = r.json().get("data", [])
                if data:
                    prices = [float(x.get("price", {}).get("grandTotal", 0.0)) for x in data if x.get("price")]
                    prices = [p for p in prices if p > 0]
                    if prices:
                        return {
                            "cash_price_total": float(min(prices)),
                            "as_of": now,
                            "source": "amadeus_test",
                        }
            except Exception:
                pass

        base = 380 + (hash(destination) % 220)
        return {
            "cash_price_total": float(base * max(travelers, 1)),
            "as_of": now,
            "source": "airfare_adapter_mock",
        }


class HotelProvider:
    def search(self, destination: str, nights: int, travelers: int) -> dict[str, Any]:
        now = _now()
        token = _amadeus_token()
        if token:
            try:
                # destination is airport code in this MVP; use as cityCode when possible.
                r = requests.get(
                    AMADEUS_HOTEL_URL,
                    params={"cityCode": destination, "adults": max(1, int(travelers)), "roomQuantity": 1},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=15,
                )
                r.raise_for_status()
                data = r.json().get("data", [])
                prices: list[float] = []
                for h in data:
                    offers = h.get("offers", [])
                    for o in offers:
                        total = o.get("price", {}).get("total")
                        if total is not None:
                            try:
                                prices.append(float(total))
                            except Exception:
                                continue
                if prices:
                    cash_rate = min(prices)
                    points_rate = int((cash_rate * max(1, nights) / 0.012))
                    fees = max(20.0, cash_rate * 0.08)
                    return {
                        "cash_rate_all_in": float(cash_rate),
                        "points_rate": points_rate,
                        "fees_on_points": float(fees),
                        "as_of": now,
                        "source": "amadeus_test",
                    }
            except Exception:
                pass

        cash_rate = float((140 + (hash(destination) % 120)) * max(nights, 1))
        points_rate = int((32000 + (hash(destination + "hotel") % 30000)) * max(nights / 5, 0.6))
        fees = float(35 + (hash(destination) % 40))
        return {
            "cash_rate_all_in": cash_rate,
            "points_rate": points_rate,
            "fees_on_points": fees,
            "as_of": now,
            "source": "hotel_adapter_mock",
        }
