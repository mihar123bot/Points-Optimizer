import uuid
from fastapi import APIRouter, HTTPException
from app.domain.models import TripSearchCreate, TripSearch
from app.store import load_trip_searches, save_trip_searches

router = APIRouter()


@router.post('', response_model=TripSearch)
def create_trip_search(payload: TripSearchCreate):
    db = load_trip_searches()
    item = TripSearch(id=str(uuid.uuid4()), payload=payload)
    db[item.id] = item.model_dump(mode="json")
    save_trip_searches(db)
    return item


@router.get('/{trip_search_id}', response_model=TripSearch)
def get_trip_search(trip_search_id: str):
    db = load_trip_searches()
    item = db.get(trip_search_id)
    if not item:
        raise HTTPException(404, 'TripSearch not found')
    return TripSearch.model_validate(item)
