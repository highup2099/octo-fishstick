from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

class QuoteCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    sell_asset: str = Field(min_length=2, max_length=30)
    buy_asset: str = Field(min_length=2, max_length=30)
    sell_amount: Decimal = Field(gt=0)
    
    @field_validator("sell_asset", "buy_asset")
    @classmethod
    def validate_asset_code(cls, v):
        """Validate asset codes contain only uppercase letters and numbers."""
        if not v or not isinstance(v, str):
            raise ValueError("Asset code must be a non-empty string")
        # Strip whitespace and convert to uppercase
        v = v.strip().upper()
        if not re.match(r"^[A-Z0-9]+$", v):
            raise ValueError("Asset code must contain only uppercase letters and numbers")
        return v
    
    @field_validator("sell_amount")
    @classmethod
    def validate_sell_amount(cls, v):
        """Validate sell amount is positive and within reasonable limits."""
        if v <= 0:
            raise ValueError("Sell amount must be positive")
        if v > Decimal("1000000000"):  # 1 billion max
            raise ValueError("Sell amount exceeds maximum allowed value")
        return v

class QuoteResponse(BaseModel):
    id: str
    sell_asset: str
    buy_asset: str
    sell_amount: Decimal
    buy_amount: Decimal
    fee_amount: Decimal
    provider: str
    status: str
    expires_at: str
