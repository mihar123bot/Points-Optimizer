import uuid
from fastapi import APIRouter, HTTPException
from app.domain.models import TripSearchCreate, TripSearch

router = APIRouter()
DB: dict[str, TripSearch] = {}


@router.post('', response_model=TripSearch)
def create_trip_search(payload: TripSearchCreate):
    item = TripSearch(id=str(uuid.uuid4()), payload=payload)
    DB[item.id] = item
    return item


@router.get('/{trip_search_id}', response_model=TripSearch)
def get_trip_search(trip_search_id: str):
    item = DB.get(trip_search_id)
    if not item:
        raise HTTPException(404, 'TripSearch not found')
    return item
