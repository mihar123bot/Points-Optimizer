import uuid
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.store import load_alerts, save_alerts

router = APIRouter()


class AlertCreate(BaseModel):
    trip_search_id: str
    type: str
    rule: str
    enabled: bool = True


class AlertUpdate(BaseModel):
    enabled: Optional[bool] = None


@router.post('')
def create_alert(payload: AlertCreate):
    db = load_alerts()
    alert_id = str(uuid.uuid4())
    db[alert_id] = {'id': alert_id, **payload.model_dump()}
    save_alerts(db)
    return db[alert_id]


@router.get('')
def list_alerts(trip_search_id: Optional[str] = None):
    vals = list(load_alerts().values())
    if trip_search_id:
        vals = [a for a in vals if a['trip_search_id'] == trip_search_id]
    return vals


@router.patch('/{alert_id}')
def update_alert(alert_id: str, payload: AlertUpdate):
    db = load_alerts()
    item = db.get(alert_id)
    if not item:
        return {'error': 'not_found'}
    for k, v in payload.model_dump(exclude_none=True).items():
        item[k] = v
    db[alert_id] = item
    save_alerts(db)
    return item
