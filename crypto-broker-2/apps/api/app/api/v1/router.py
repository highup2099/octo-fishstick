"""API v1 Router - Aggregates all v1 endpoints."""
from fastapi import APIRouter
from .quotes import router as quotes_router
from .orders import router as orders_router

router = APIRouter(prefix="/api/v1")

# Include sub-routers (they already have their own prefixes)
router.include_router(quotes_router)  # /api/v1/quotes
router.include_router(orders_router)  # /api/v1/orders

