from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.models import RecommendationBundle, RecommendationOption
from app.services.scoring import blended_score
from app.services.recommender import generate_destination_candidates
from app.store import load_trip_searches

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
    candidates = generate_destination_candidates(payload)
    if not candidates:
        raise HTTPException(422, "No destinations meet constraints")

    now = datetime.now(timezone.utc).isoformat()
    options = []
    for i, c in enumerate(candidates[:8], start=1):
        oop = round(700 + i * 120 + c["stops"] * 100 + c["travel_hours"] * 20, 2)
        cpp_f = round(1.3 + (8 - i) * 0.1, 2)
        cpp_h = round(1.4 + (i % 4) * 0.1, 2)
        cpp_blended = min(round((cpp_f + cpp_h) / 2, 2), 5.0)
        friction = c["stops"] * 2 + max(0, c["travel_hours"] - 7) * 0.5
        score = blended_score(oop, cpp_blended, friction)
        options.append(
            RecommendationOption(
                id=f"opt-{i}",
                destination=c["code"],
                oop_total=oop,
                cpp_flight=cpp_f,
                cpp_hotel=cpp_h,
                cpp_blended_capped=cpp_blended,
                score_final=score,
                rationale=[
                    f"{c['stops']} stop(s)",
                    f"{c['travel_hours']}h total travel",
                    "Transparent CPP/OOP scoring",
                ],
                as_of=now,
            )
        )

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
