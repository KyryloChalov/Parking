from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Literal

# Allowed rate names
ALLOWED_RATE_NAMES = ["hourly", "daily", "monthly", "custom"]

class RateSchema(BaseModel):
    rate_name: Literal["hourly", "daily", "monthly", "custom"]
    price: int

    @validator("rate_name")
    def validate_rate_name(cls, value):
        if value not in ALLOWED_RATE_NAMES:
            raise ValueError(f"Rate name must be one of {ALLOWED_RATE_NAMES}")
        return value

class RateResponseSchema(BaseModel):
    id: int
    rate_name: str
    price: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True

class RateUpdateSchema(BaseModel):
    price: int
    