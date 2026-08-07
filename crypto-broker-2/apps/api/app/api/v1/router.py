from fastapi import APIRouter
from .quotes import router as quotes_router
from .orders import router as orders_router

router = APIRouter()
router.include_router(quotes_router, prefix="/quotes", tags=["quotes"])
router.include_router(orders_router, prefix="/orders", tags=["orders"])
