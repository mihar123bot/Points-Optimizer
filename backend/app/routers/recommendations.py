from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.models import RecommendationBundle, RecommendationOption
from app.services.scoring import blended_score
from app.services.recommender import generate_destination_candidates
from app.store import load_trip_searches, load_recommendations, save_recommendations
from app.adapters.providers import AwardProvider, AirfareProvider, HotelProvider

router = APIRouter()


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
        marriott_cpp_eligible = cpp_hotel >= 1.5

        hotel_cash_component = 0.0 if marriott_cpp_eligible else hotel_cash
        hotel_mode = "points" if marriott_cpp_eligible else "cash"
        oop_total = round(taxes_fees + hotel_cash_component, 2)

        cpp_blended = min(round((cpp_flight + max(cpp_hotel, 0.0)) / 2.0, 2), 5.0)
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
                    f"Hotel booking mode: {hotel_mode}",
                ],
                as_of=now,
                points_breakdown={
                    "flight_program": suggested_flight_program,
                    "flight_points": flight_points_required,
                    "hotel_program": "MARRIOTT",
                    "hotel_points": hotel_points_required,
                    "taxes_fees": round(taxes_fees, 2),
                },
                friction_components=friction_components,
                score_components=score_components,
                marriott_points_eligible=marriott_cpp_eligible,
                hotel_booking_mode=hotel_mode,
                source_timestamps={
                    "award": award["as_of"],
                    "airfare": airfare["as_of"],
                    "hotel": hotel["as_of"],
                },
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
    }
    return RecommendationBundle(trip_search_id=req.trip_search_id, winner_tiles=winner_tiles, options=options_sorted)
