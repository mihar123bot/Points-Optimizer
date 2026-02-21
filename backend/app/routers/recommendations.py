from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from app.domain.models import RecommendationBundle, RecommendationOption
from app.services.scoring import blended_score

router = APIRouter()


class GenerateRequest(BaseModel):
    trip_search_id: str


@router.post('/generate', response_model=RecommendationBundle)
def generate_recommendations(req: GenerateRequest):
    now = datetime.now(timezone.utc).isoformat()
    options = [
        RecommendationOption(
            id='opt-1', destination='CUN', oop_total=980.0, cpp_flight=1.8, cpp_hotel=1.6,
            cpp_blended_capped=1.7, score_final=blended_score(980.0, 1.7, 2.0),
            rationale=['Low OOP', 'Direct options available'], as_of=now,
        ),
        RecommendationOption(
            id='opt-2', destination='PUJ', oop_total=840.0, cpp_flight=1.5, cpp_hotel=1.7,
            cpp_blended_capped=1.6, score_final=blended_score(840.0, 1.6, 2.5),
            rationale=['Best OOP', '1 stop only'], as_of=now,
        ),
        RecommendationOption(
            id='opt-3', destination='LIS', oop_total=1220.0, cpp_flight=2.2, cpp_hotel=1.4,
            cpp_blended_capped=2.0, score_final=blended_score(1220.0, 2.0, 3.5),
            rationale=['High flight CPP', 'Longer route'], as_of=now,
        ),
    ]
    winner_tiles = {
        'best_oop': 'opt-2',
        'best_cpp': 'opt-3',
        'best_business': 'opt-3',
        'best_balanced': max(options, key=lambda x: x.score_final).id,
    }
    return RecommendationBundle(trip_search_id=req.trip_search_id, winner_tiles=winner_tiles, options=options)
