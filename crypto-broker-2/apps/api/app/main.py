from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.v1.router import router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.4.0",
    docs_url="/docs" if settings.app_env != "production" else None,
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Strict CORS configuration for production
if settings.app_env == "production":
    # In production, only allow specific origins from environment variable
    allowed_origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
else:
    # Development origins
    allowed_origins = ["http://localhost:3000", "http://localhost:3001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Explicit methods instead of wildcard
    allow_headers=["Authorization", "Content-Type"],  # Explicit headers instead of wildcard
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=600,  # Cache preflight for 10 minutes
)
app.include_router(router, prefix="/api/v1")
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.app_env}
