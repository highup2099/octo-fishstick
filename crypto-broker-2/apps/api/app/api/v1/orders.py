from uuid import UUID
from fastapi import APIRouter
from app.schemas.orders import OrderCreate, OrderResponse

router = APIRouter()

@router.post("", response_model=OrderResponse)
async def create_order(payload: OrderCreate):
    # Next slice: persist Order, run risk state, then enqueue orchestration.
    return {"id": payload.quote_id, "status": "created"}
