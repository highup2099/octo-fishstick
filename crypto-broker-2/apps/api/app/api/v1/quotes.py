import logging
from fastapi import APIRouter, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.quotes import QuoteCreate, QuoteResponse
from app.services.quote_service import QuoteService
from app.core.security import get_current_active_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter()
service = QuoteService()
# Create a local limiter instance for this module
limiter = Limiter(key_func=get_remote_address)

@router.post("", response_model=QuoteResponse)
@limiter.limit("30/minute")  # Rate limit: 30 quotes per minute per IP
async def create_quote(
    payload: QuoteCreate,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Create a new quote for currency exchange.
    Requires authentication and rate limiting to prevent abuse.
    """
    logger.info(f"Quote request received from user {current_user.user_id}: {payload}")
    result = await service.create(payload, current_user)
    return result
