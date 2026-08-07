from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel, Field
from uuid import UUID
from app.core.config import settings

class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: datetime
    iat: datetime
    
class TokenData(BaseModel):
    user_id: UUID
    username: Optional[str] = None

security = HTTPBearer()

def create_access_token(user_id: UUID, username: Optional[str] = None, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token for authenticated user."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    if username:
        payload["username"] = username
    
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(user_id=UUID(user_id), username=payload.get("username"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid user ID format: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Dependency to get current authenticated user from JWT token."""
    token = credentials.credentials
    return decode_token(token)

async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Dependency to ensure user is active (can be extended with DB check)."""
    # TODO: Add DB lookup to verify user exists and is_active=True
    # For now, just return the decoded token data
    return current_user
