from fastapi import APIRouter
from pydantic import BaseModel
from app.domain.models import PlaybookResponse

router = APIRouter()


class PlaybookRequest(BaseModel):
    option_id: str


@router.post('/generate', response_model=PlaybookResponse)
def generate_playbook(req: PlaybookRequest):
    return PlaybookResponse(
        option_id=req.option_id,
        transfer_steps=[
            'Verify award seats still available before transfer',
            'Transfer required points from MR/CAP1 to selected partner',
        ],
        booking_steps=[
            'Book flight segment first',
            'Book hotel after ticket confirmation',
        ],
        warnings=['Transfers are irreversible', 'Award space can disappear quickly'],
        fallbacks=['Try +/-1 day', 'Try alternate origin airport'],
    )
