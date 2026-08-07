from uuid import UUID
from pydantic import BaseModel

class OrderCreate(BaseModel):
    quote_id: UUID

class OrderResponse(BaseModel):
    id: UUID
    status: str
