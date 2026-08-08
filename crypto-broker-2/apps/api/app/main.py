import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
from app.core.config import settings
from app.db import engine
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Base

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Starting up CryptoBroker API...")
    async with engine.begin() as conn:
        logger.info("Database connection established")
    yield
    # Shutdown
    logger.info("Shutting down CryptoBroker API...")
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.4.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Mini App
        "http://localhost:3001",  # Admin Dashboard
        "http://localhost:8080",  # Caddy proxy
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router (already has /api/v1 prefix)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.app_env}
