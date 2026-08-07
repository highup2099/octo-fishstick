from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict

class OrderCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    quote_id: UUID
    
    @field_validator("quote_id")
    @classmethod
    def validate_quote_id(cls, v):
        """Validate quote_id is a valid UUID."""
        if not v:
            raise ValueError("quote_id is required")
        return v

class OrderResponse(BaseModel):
    id: UUID
    status: str
    user_id: UUID | None = None  # Added for audit purposes
    quote_id: UUID | None = None  # Include quote_id in response
    risk_status: str | None = None  # Risk check status
    created_at: str | None = None  # Timestamp
