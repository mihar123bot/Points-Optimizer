from datetime import datetime, timezone
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.models import RecommendationBundle, RecommendationOption
from app.services.scoring import blended_score
from app.services.recommender import generate_destination_candidates
from app.store import load_trip_searches, load_recommendations, save_recommendations
from app.adapters.providers import AwardProvider, AirfareProvider, HotelProvider

router = APIRouter()

_RECO_CACHE: dict[str, tuple[float, dict]] = {}
_CACHE_TTL_SECONDS = 300


class GenerateRequest(BaseModel):
    trip_search_id: str


@router.post('/generate', response_model=RecommendationBundle)
def generate_recommendations(req: GenerateRequest):
    trip_searches = load_trip_searches()
    trip = trip_searches.get(req.trip_search_id)
    if not trip:
        raise HTTPException(404, "TripSearch not found")

    payload = trip["payload"]

    us_origin_allowlist = {"IAD", "DCA", "BWI", "JFK", "EWR", "BOS", "LAX", "SFO", "ORD", "ATL", "MIA", "DFW", "SEA"}
    origins = [str(x).upper() for x in payload.get("origins", [])]
    if not origins or any(o not in us_origin_allowlist for o in origins):
        raise HTTPException(422, "MVP currently supports US departure airports only")

    cache_key = str({
        "trip_search_id": req.trip_search_id,
        "origins": payload.get("origins"),
        "start": payload.get("date_window_start"),
        "end": payload.get("date_window_end"),
        "nights": payload.get("duration_nights"),
        "travelers": payload.get("travelers"),
        "cabin": payload.get("cabin_preference"),
        "vibe": payload.get("vibe_tags"),
        "preferred": payload.get("preferred_destinations"),
        "constraints": payload.get("constraints"),
    })
    now_ts = time.time()
    cached = _RECO_CACHE.get(cache_key)
    if cached and (now_ts - cached[0] <= _CACHE_TTL_SECONDS):
        cached_bundle = dict(cached[1])
        cached_bundle["winner_tiles"] = dict(cached_bundle.get("winner_tiles", {}))
        cached_bundle["winner_tiles"]["_meta_cache"] = "HIT"
        return RecommendationBundle.model_validate(cached_bundle)

    candidates = generate_destination_candidates(payload)
    if not candidates:
        raise HTTPException(422, "No destinations meet constraints")

    balances = {b.get("program"): int(b.get("balance", 0)) for b in payload.get("balances", [])}
    travelers = int(payload.get("travelers", 2))
    nights = int(payload.get("duration_nights", 5))
    cabin = str(payload.get("cabin_preference", "economy"))
    origin = payload.get("origins", ["IAD"])[0]
    depart_date = str(payload.get("date_window_start"))
    return_date = str(payload.get("date_window_end"))

    award_provider = AwardProvider()
    airfare_provider = AirfareProvider()
    hotel_provider = HotelProvider()

    rec_store = load_recommendations()
    options = []
    now = datetime.now(timezone.utc).isoformat()

    for i, c in enumerate(candidates[:8], start=1):
        destination = c["code"]
        award = award_provider.search(origin, destination, travelers, cabin=cabin)
        airfare = airfare_provider.search(origin, destination, travelers, depart_date=depart_date, return_date=return_date)
        hotel = hotel_provider.search(destination, nights, travelers)

        flight_points_required = int(award["points_cost"])
        taxes_fees = float(award["taxes_fees"])
        cash_flight = float(airfare["cash_price_total"])

        hotel_points_required = int(hotel["points_rate"])
        hotel_cash = float(hotel["cash_rate_all_in"])
        hotel_fees_on_points = float(hotel["fees_on_points"])

        cpp_flight = ((cash_flight - taxes_fees) / max(flight_points_required, 1)) * 100.0
        cpp_hotel = ((hotel_cash - hotel_fees_on_points) / max(hotel_points_required, 1)) * 100.0

        cpp_threshold = 1.0
        flight_cpp_ok = cpp_flight > cpp_threshold
        hotel_cpp_ok = cpp_hotel > cpp_threshold

        cash_flights_mode = "LIVE" if airfare.get("source") == "amadeus_test" else "ESTIMATED"
        cash_hotels_mode = "LIVE" if hotel.get("source") == "amadeus_test" else "ESTIMATED"
        award_mode = "LIVE" if award.get("source") == "seats_aero_live" else "ESTIMATED"
        award_live = award_mode == "LIVE"

        # P0 rule: prefer points on flights when live award inventory exists and CPP>1.0.
        if award_live and flight_cpp_ok:
            use_points_for = "flight"
        elif hotel_cpp_ok and ((not award_live) or (not flight_cpp_ok)):
            use_points_for = "hotel"
        elif flight_cpp_ok:
            use_points_for = "flight"
        else:
            use_points_for = "none"

        points_strategy_alternates = []
        if award_live and flight_cpp_ok and hotel_cpp_ok:
            points_strategy_alternates = ["flight", "hotel"]

        if use_points_for == "flight":
            oop_total = round(taxes_fees + hotel_cash, 2)
        elif use_points_for == "hotel":
            oop_total = round(cash_flight + hotel_fees_on_points, 2)
        else:
            oop_total = round(cash_flight + hotel_cash, 2)

        hotel_mode = "points" if use_points_for == "hotel" else "cash"
        marriott_cpp_eligible = hotel_cpp_ok

        cpp_blended = min(round((cpp_flight + max(cpp_hotel, 0.0)) / 2.0, 2), 5.0)
        if award_live:
            cpp_blended = min(5.0, round(cpp_blended + 0.15, 2))
        friction_components = {
            "stops_penalty": c["stops"] * 2.0,
            "travel_time_penalty": max(0.0, c["travel_hours"] - 7.0) * 0.5,
        }
        friction = friction_components["stops_penalty"] + friction_components["travel_time_penalty"]

        score = blended_score(oop_total, cpp_blended, friction)
        score_components = {
            "oop_term": round(-oop_total / 5000.0, 4),
            "cpp_term": round(min(cpp_blended, 5.0) / 5.0, 4),
            "friction_term": round(-friction / 10.0, 4),
            "weights": {"w1": 0.5, "w2": 0.35, "w3": 0.15},
        }

        option_id = f"{req.trip_search_id[:8]}-opt-{i}"
        suggested_flight_program = "MR" if balances.get("MR", 0) >= balances.get("CAP1", 0) else "CAP1"

        validation_steps = [
            f"Open the award source/site for {award.get('program', 'program search')}.",
            f"Search {origin} → {destination} in {cabin} cabin for {depart_date} (and return {return_date} if round trip).",
            f"Compare points ({flight_points_required}) and taxes/fees (${taxes_fees:.2f}) with this result.",
            f"Confirm as-of timestamp: {award.get('retrieved_at', now)}.",
        ]

        rec_store[option_id] = {
            "option_id": option_id,
            "trip_search_id": req.trip_search_id,
            "destination": destination,
            "stops": c["stops"],
            "travel_hours": c["travel_hours"],
            "oop_total": oop_total,
            "cpp_flight": cpp_flight,
            "cpp_hotel": cpp_hotel,
            "flight_points_required": flight_points_required,
            "hotel_points_required": hotel_points_required,
            "taxes_fees": taxes_fees,
            "suggested_flight_program": suggested_flight_program,
            "marriott_cpp_eligible": marriott_cpp_eligible,
            "hotel_booking_mode": hotel_mode,
            "points_strategy": use_points_for,
            "points_strategy_alternates": points_strategy_alternates,
            "cpp_threshold": cpp_threshold,
            "cash_flights_mode": cash_flights_mode,
            "cash_hotels_mode": cash_hotels_mode,
            "award_mode": award_mode,
            "award_details": {
                "program": award.get("program"),
                "cabin": cabin,
                "points": flight_points_required,
                "taxes_fees": taxes_fees,
                "availability": award.get("availability_indicator", "unknown"),
                "retrieved_at": award.get("retrieved_at", now),
                "source_label": award.get("source", "unknown"),
                "source_url": award.get("source_url", ""),
            },
            "validation_steps": validation_steps,
            "as_of": now,
        }

        options.append(
            RecommendationOption(
                id=option_id,
                destination=destination,
                oop_total=oop_total,
                cpp_flight=round(cpp_flight, 2),
                cpp_hotel=round(cpp_hotel, 2),
                cpp_blended_capped=cpp_blended,
                score_final=score,
                rationale=[
                    f"{c['stops']} stop(s)",
                    f"{c['travel_hours']}h total travel",
                    f"Points strategy: {use_points_for}",
                    f"Award mode: {award_mode}",
                ],
                as_of=now,
                points_breakdown={
                    "flight_program": suggested_flight_program,
                    "flight_points": flight_points_required,
                    "hotel_program": "MARRIOTT",
                    "hotel_points": hotel_points_required,
                    "taxes_fees": round(taxes_fees, 2),
                    "flight_cpp": round(cpp_flight, 3),
                    "hotel_cpp": round(cpp_hotel, 3),
                    "cpp_threshold": cpp_threshold,
                    "points_strategy": use_points_for,
                    "points_strategy_alternates": points_strategy_alternates,
                },
                friction_components=friction_components,
                score_components=score_components,
                marriott_points_eligible=marriott_cpp_eligible,
                hotel_booking_mode=hotel_mode,
                points_strategy=use_points_for,
                cpp_threshold=cpp_threshold,
                cash_flights_mode=cash_flights_mode,
                cash_hotels_mode=cash_hotels_mode,
                award_mode=award_mode,
                award_details={
                    "program": award.get("program"),
                    "cabin": cabin,
                    "points": flight_points_required,
                    "taxes_fees": round(taxes_fees, 2),
                    "availability": award.get("availability_indicator", "unknown"),
                    "retrieved_at": award.get("retrieved_at", now),
                    "source_label": award.get("source", "unknown"),
                    "source_url": award.get("source_url", ""),
                },
                validation_steps=validation_steps,
                source_timestamps={
                    "award": award["as_of"],
                    "airfare": airfare["as_of"],
                    "hotel": hotel["as_of"],
                },
                source_labels={
                    "award": award.get("source", "unknown"),
                    "airfare": airfare.get("source", "unknown"),
                    "hotel": hotel.get("source", "unknown"),
                },
                api_mode=(
                    "live"
                    if (cash_flights_mode == "LIVE" or cash_hotels_mode == "LIVE" or award_mode == "LIVE")
                    else "fallback"
                ),
            )
        )

    save_recommendations(rec_store)

    options_sorted = sorted(options, key=lambda x: x.score_final, reverse=True)
    best_oop = min(options, key=lambda x: x.oop_total).id
    best_cpp = max(options, key=lambda x: x.cpp_blended_capped).id
    winner_tiles = {
        'best_oop': best_oop,
        'best_cpp': best_cpp,
        'best_business': best_cpp,
        'best_balanced': options_sorted[0].id,
        '_meta_cache': 'MISS',
    }
    bundle = RecommendationBundle(trip_search_id=req.trip_search_id, winner_tiles=winner_tiles, options=options_sorted)
    _RECO_CACHE[cache_key] = (time.time(), bundle.model_dump(mode="json"))
    return bundle
