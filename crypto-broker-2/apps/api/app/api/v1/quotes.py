from fastapi import APIRouter
from app.schemas.quotes import QuoteCreate, QuoteResponse
from app.services.quote_service import QuoteService

router = APIRouter()
service = QuoteService()

@router.post("", response_model=QuoteResponse)
async def create_quote(payload: QuoteCreate):
    return await service.create(payload.sell_asset, payload.buy_asset, payload.sell_amount)
