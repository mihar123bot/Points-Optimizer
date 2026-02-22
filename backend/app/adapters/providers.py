from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

import requests

AMADEUS_AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_FLIGHT_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"
AMADEUS_HOTEL_URL = "https://test.api.amadeus.com/v3/shopping/hotel-offers"

# Realistic per-route data: cash prices (per person round trip), points, airlines, duration
ROUTE_DATA: dict[str, dict] = {
    "CUN": {
        "city": "Cancún", "country": "Mexico",
        "cash_pp_base": 380, "cash_pp_range": 120,
        "pts_economy": 22000, "pts_business": 68000,
        "taxes_base": 48, "taxes_range": 30,
        "duration": "3h 45m", "airlines": ["American", "United", "Delta"],
    },
    "PUJ": {
        "city": "Punta Cana", "country": "Dominican Republic",
        "cash_pp_base": 430, "cash_pp_range": 110,
        "pts_economy": 28000, "pts_business": 80000,
        "taxes_base": 55, "taxes_range": 35,
        "duration": "4h 30m", "airlines": ["JetBlue", "American", "United"],
    },
    "NAS": {
        "city": "Nassau", "country": "Bahamas",
        "cash_pp_base": 330, "cash_pp_range": 90,
        "pts_economy": 20000, "pts_business": 60000,
        "taxes_base": 42, "taxes_range": 25,
        "duration": "3h 10m", "airlines": ["American", "Delta", "JetBlue"],
    },
    "SJD": {
        "city": "Los Cabos", "country": "Mexico",
        "cash_pp_base": 460, "cash_pp_range": 160,
        "pts_economy": 35000, "pts_business": 90000,
        "taxes_base": 65, "taxes_range": 40,
        "duration": "6h 10m", "airlines": ["American", "United", "Alaska"],
    },
    "YVR": {
        "city": "Vancouver", "country": "Canada",
        "cash_pp_base": 350, "cash_pp_range": 110,
        "pts_economy": 25000, "pts_business": 75000,
        "taxes_base": 52, "taxes_range": 30,
        "duration": "5h 55m", "airlines": ["Air Canada", "Alaska", "United"],
    },
    "EZE": {
        "city": "Buenos Aires", "country": "Argentina",
        "cash_pp_base": 860, "cash_pp_range": 200,
        "pts_economy": 55000, "pts_business": 120000,
        "taxes_base": 95, "taxes_range": 55,
        "duration": "10h 15m", "airlines": ["LATAM", "American", "United"],
    },
    "LIM": {
        "city": "Lima", "country": "Peru",
        "cash_pp_base": 640, "cash_pp_range": 160,
        "pts_economy": 42000, "pts_business": 100000,
        "taxes_base": 75, "taxes_range": 45,
        "duration": "8h 0m", "airlines": ["LATAM", "American", "United"],
    },
    "CDG": {
        "city": "Paris", "country": "France",
        "cash_pp_base": 750, "cash_pp_range": 220,
        "pts_economy": 50000, "pts_business": 110000,
        "taxes_base": 120, "taxes_range": 60,
        "duration": "7h 50m", "airlines": ["Air France", "United", "Delta"],
    },
    "FCO": {
        "city": "Rome", "country": "Italy",
        "cash_pp_base": 790, "cash_pp_range": 220,
        "pts_economy": 52000, "pts_business": 115000,
        "taxes_base": 115, "taxes_range": 55,
        "duration": "8h 45m", "airlines": ["ITA Airways", "United", "Delta"],
    },
    "LHR": {
        "city": "London", "country": "United Kingdom",
        "cash_pp_base": 700, "cash_pp_range": 210,
        "pts_economy": 48000, "pts_business": 105000,
        "taxes_base": 130, "taxes_range": 65,
        "duration": "7h 15m", "airlines": ["British Airways", "Virgin Atlantic", "United"],
    },
    "KEF": {
        "city": "Reykjavík", "country": "Iceland",
        "cash_pp_base": 440, "cash_pp_range": 160,
        "pts_economy": 28000, "pts_business": 75000,
        "taxes_base": 58, "taxes_range": 35,
        "duration": "5h 55m", "airlines": ["Icelandair", "United", "Delta"],
    },
    "ATH": {
        "city": "Athens", "country": "Greece",
        "cash_pp_base": 840, "cash_pp_range": 200,
        "pts_economy": 55000, "pts_business": 120000,
        "taxes_base": 110, "taxes_range": 55,
        "duration": "9h 45m", "airlines": ["Aegean Airlines", "United", "Delta"],
    },
    "HND": {
        "city": "Tokyo", "country": "Japan",
        "cash_pp_base": 900, "cash_pp_range": 320,
        "pts_economy": 60000, "pts_business": 130000,
        "taxes_base": 85, "taxes_range": 45,
        "duration": "13h 30m", "airlines": ["JAL", "ANA", "United"],
    },
    "BKK": {
        "city": "Bangkok", "country": "Thailand",
        "cash_pp_base": 950, "cash_pp_range": 320,
        "pts_economy": 65000, "pts_business": 140000,
        "taxes_base": 90, "taxes_range": 50,
        "duration": "18h 0m", "airlines": ["Thai Airways", "EVA Air", "United"],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pick(items: list, seed: int) -> Any:
    return items[abs(seed) % len(items)]


# Program-specific target CPP (cents per point) used for award estimation.
# These reflect realistic sweet-spot redemption values per program.
PROGRAM_CPP: dict[str, dict[str, float]] = {
    "MR": {"economy": 1.7, "premium_economy": 1.9, "business": 2.1, "first": 2.3},
    "CAP1": {"economy": 1.7, "premium_economy": 1.9, "business": 2.0, "first": 2.2},
    "MARRIOTT": {"economy": 0.8, "premium_economy": 0.9, "business": 1.0, "first": 1.1},
}


SEATS_AERO_SEARCH_URL = "https://seats.aero/partnerapi/search"
SEATS_AERO_TRIPS_URL  = "https://seats.aero/partnerapi/trips"

_token_cache: dict[str, Any] = {"token": None, "expires_at": 0.0}

# Per-source provider caches (TTLs per PRD §11)
_AWARD_CACHE: dict[str, tuple[float, dict]] = {}
_AIRFARE_CACHE: dict[str, tuple[float, dict]] = {}
_AWARD_CACHE_TTL   = 7200    # 2 hours — Seats.aero
_AIRFARE_CACHE_TTL = 43200   # 12 hours — Amadeus flights

# Seats.aero source → human-readable program name mapping (partial)
_SEATS_SOURCE_TO_PROGRAM: dict[str, str] = {
    "aeroplan":       "Air Canada Aeroplan",
    "flyingblue":     "Flying Blue",
    "united":         "United MileagePlus",
    "delta":          "Delta SkyMiles",
    "american":       "American AAdvantage",
    "jetblue":        "JetBlue TrueBlue",
    "alaska":         "Alaska Mileage Plan",
    "lifemiles":      "Avianca LifeMiles",
    "britishairways": "British Airways Avios",
    "ana":            "ANA Mileage Club",
    "virginatlantic": "Virgin Atlantic Flying Club",
    "singapore":      "Singapore KrisFlyer",
    "turkish":        "Turkish Miles&Smiles",
    "emirates":       "Emirates Skywards",
    "qantas":         "Qantas Frequent Flyer",
    "qatar":          "Qatar Airways Avios",
}


def _amadeus_token() -> str | None:
    cid = os.getenv("AMADEUS_CLIENT_ID")
    csec = os.getenv("AMADEUS_CLIENT_SECRET")
    if not cid or not csec:
        return None
    # Return cached token if it has more than 60 seconds left
    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["token"]
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
        data = r.json()
        token = data.get("access_token")
        expires_in = int(data.get("expires_in", 1799))
        _token_cache["token"] = token
        _token_cache["expires_at"] = time.time() + expires_in
        return token
    except Exception:
        return None


class AwardProvider:
    """Award inventory: tries Seats.aero live API, then falls back to per-route estimator."""

    def search(
        self,
        origin: str,
        destination: str,
        travelers: int,
        cabin: str = "economy",
        depart_date: str = "",
        return_date: str = "",
    ) -> dict[str, Any]:
        now = _now()
        now_ts = time.time()
        route = ROUTE_DATA.get(destination, {})
        seed = hash(origin + destination)

        # Map cabin to Seats.aero response field prefix (Y/W/J/F)
        cabin_prefix_map = {
            "economy": "Y", "premium_economy": "W", "business": "J", "first": "F",
        }
        cabin_prefix = cabin_prefix_map.get(cabin, "Y")

        seats_key = os.getenv("SEATS_AERO_API_KEY")
        if seats_key and depart_date:
            cache_key = f"{origin}:{destination}:{cabin_prefix}:{depart_date}"
            cached = _AWARD_CACHE.get(cache_key)
            if cached and (now_ts - cached[0]) < _AWARD_CACHE_TTL:
                return cached[1]

            try:
                r = requests.get(
                    SEATS_AERO_SEARCH_URL,
                    params={
                        "origin_airport":      origin,
                        "destination_airport": destination,
                        "start_date":          depart_date,
                        "end_date":            return_date or depart_date,
                    },
                    headers={"Partner-Authorization": seats_key},
                    timeout=15,
                )
                r.raise_for_status()
                payload = r.json()
                items = payload.get("data", [])

                # Filter to items with availability for the requested cabin
                avail_field = f"{cabin_prefix}Available"
                cost_field  = f"{cabin_prefix}MileageCostRaw"
                tax_field   = f"{cabin_prefix}TotalTaxesRaw"

                available_items = [
                    x for x in items
                    if x.get(avail_field) is True
                    and (x.get(cost_field) or 0) > 0
                    # Only trust USD taxes
                    and x.get("TaxesCurrency", "USD") == "USD"
                ]

                # Fall back to any cabin if preferred cabin unavailable
                if not available_items:
                    available_items = [
                        x for x in items
                        if (x.get("YAvailable") or x.get("JAvailable") or x.get("WAvailable") or x.get("FAvailable"))
                        and x.get("TaxesCurrency", "USD") == "USD"
                    ]
                    # Re-map to economy prefix if falling back
                    if available_items:
                        cabin_prefix = "Y"
                        cost_field   = "YMileageCostRaw"
                        tax_field    = "YTotalTaxesRaw"

                if available_items:
                    # Pick cheapest by mileage cost for requested cabin
                    best = min(available_items, key=lambda x: int(x.get(cost_field) or 999_999_999))

                    points = int(best.get(cost_field) or 0)
                    # Taxes stored in cents in Seats.aero response
                    taxes_raw = best.get(tax_field) or 0
                    taxes = round(float(taxes_raw) / 100.0, 2)

                    src_program = str(best.get("Source") or "")
                    program_label = _SEATS_SOURCE_TO_PROGRAM.get(src_program.lower(), src_program.upper() or "MR")

                    # Use UpdatedAt for data freshness
                    updated_at_str = best.get("UpdatedAt", "")
                    retrieved_at_ts = now_ts
                    if updated_at_str:
                        try:
                            dt = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                            retrieved_at_ts = dt.timestamp()
                        except Exception:
                            pass

                    # Extract operating airline from YAirlines field (comma-sep IATA codes)
                    airlines_str = str(best.get("YAirlines") or "")
                    operating_carrier = airlines_str.split(",")[0].strip() if airlines_str else ""

                    # Optionally fetch flight-level data for exact matching
                    avail_id = best.get("ID") or ""
                    flight_number = ""
                    exact_match = False
                    if avail_id:
                        try:
                            tr = requests.get(
                                SEATS_AERO_TRIPS_URL,
                                params={"id": avail_id},
                                headers={"Partner-Authorization": seats_key},
                                timeout=10,
                            )
                            tr.raise_for_status()
                            trips = tr.json()
                            segs = trips if isinstance(trips, list) else trips.get("data", [])
                            if segs:
                                first_seg = segs[0]
                                flight_number = str(first_seg.get("FlightNumber") or "")
                                if not operating_carrier:
                                    operating_carrier = str(first_seg.get("OperatingCarrier") or "")
                                exact_match = bool(flight_number)
                        except Exception:
                            pass

                    if points > 0:
                        result = {
                            "points_cost":            points,
                            "taxes_fees":             taxes,
                            "program":                program_label,
                            "availability_indicator": "available",
                            "source_url":             "",
                            "retrieved_at":           now,
                            "as_of":                  now,
                            "source":                 "seats_aero_live",
                            "airline":                operating_carrier or route.get("airlines", [""])[0],
                            "duration":               route.get("duration", ""),
                            "city_name":              route.get("city", destination),
                            # Matching metadata (PRD §6 / confidence scoring)
                            "operating_carrier":      operating_carrier,
                            "flight_number":          flight_number,
                            "exact_flight_match":     exact_match,
                            "retrieved_at_ts":        retrieved_at_ts,
                        }
                        _AWARD_CACHE[cache_key] = (now_ts, result)
                        return result
            except Exception:
                pass

        # ── Per-route estimator (fallback) ────────────────────────────────────
        cabin_key = cabin if cabin in ("economy", "premium_economy", "business", "first") else "economy"
        target_cpp = PROGRAM_CPP["MR"].get(cabin_key, 1.7)

        cash_pp_base = route.get("cash_pp_base", 400)
        cash_pp_var  = max(1, route.get("cash_pp_range", 150))
        est_cash_pp  = cash_pp_base + (abs(seed) % cash_pp_var)

        taxes_base = route.get("taxes_base", 80)
        taxes_var  = max(1, route.get("taxes_range", 40))
        taxes = float(taxes_base + (abs(seed) % taxes_var))

        pts = int((est_cash_pp - taxes) / target_cpp * 100)

        pts_key   = "pts_business" if cabin in ("business", "first") else "pts_economy"
        chart_pts = route.get(pts_key, pts)
        pts       = int(pts * 0.4 + chart_pts * 0.6) if chart_pts else pts

        airline = _pick(route.get("airlines", ["United"]), seed)

        return {
            "points_cost":            max(10000, pts),
            "taxes_fees":             taxes,
            "program":                "MR",
            "availability_indicator": "estimated",
            "source_url":             "",
            "retrieved_at":           now,
            "as_of":                  now,
            "source":                 "award_estimator_mvp",
            "airline":                airline,
            "duration":               route.get("duration", ""),
            "city_name":              route.get("city", destination),
            # Matching metadata (empty for estimator)
            "operating_carrier":      "",
            "flight_number":          "",
            "exact_flight_match":     False,
            "retrieved_at_ts":        now_ts,
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
        now_ts = time.time()
        route = ROUTE_DATA.get(destination, {})
        seed = hash(origin + destination)

        cache_key = f"{origin}:{destination}:{depart_date}:{travelers}"
        cached = _AIRFARE_CACHE.get(cache_key)
        if cached and (now_ts - cached[0]) < _AIRFARE_CACHE_TTL:
            return cached[1]

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
                    best = None
                    best_price = float("inf")
                    for offer in data:
                        price = float(offer.get("price", {}).get("grandTotal", 0) or 0)
                        if 0 < price < best_price:
                            best_price = price
                            best = offer
                    if best and best_price > 0:
                        # Extract airline and duration from first itinerary
                        itineraries = best.get("itineraries", [])
                        airline = ""
                        duration_str = ""
                        if itineraries:
                            segments = itineraries[0].get("segments", [])
                            if segments:
                                carrier = segments[0].get("carrierCode", "")
                                airline = carrier  # raw IATA code; map to name below
                            raw_dur = itineraries[0].get("duration", "")
                            if raw_dur.startswith("PT"):
                                raw_dur = raw_dur[2:]
                                h = raw_dur.split("H")[0] if "H" in raw_dur else "0"
                                m = raw_dur.split("H")[-1].replace("M", "") if "M" in raw_dur else "0"
                                duration_str = f"{h}h {m}m"
                        price_pp = round(best_price / max(travelers, 1), 2)
                        result = {
                            "cash_price_total": best_price,
                            "cash_price_pp": price_pp,
                            "airline": airline or route.get("airlines", [""])[0],
                            "duration": duration_str or route.get("duration", ""),
                            "city_name": route.get("city", destination),
                            "country": route.get("country", ""),
                            "as_of": now,
                            "source": "amadeus_test",
                        }
                        _AIRFARE_CACHE[cache_key] = (now_ts, result)
                        return result
            except Exception:
                pass

        # Per-route mock with deterministic but realistic pricing
        base = route.get("cash_pp_base", 400)
        var = max(1, route.get("cash_pp_range", 150))
        price_pp = base + (abs(seed) % var)
        airline = _pick(route.get("airlines", ["United"]), seed)

        return {
            "cash_price_total": float(price_pp * max(travelers, 1)),
            "cash_price_pp": float(price_pp),
            "airline": airline,
            "duration": route.get("duration", ""),
            "city_name": route.get("city", destination),
            "country": route.get("country", ""),
            "as_of": now,
            "source": "airfare_adapter_mock",
        }


class HotelProvider:
    def search(self, destination: str, nights: int, travelers: int) -> dict[str, Any]:
        now = _now()
        token = _amadeus_token()
        if token:
            try:
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
