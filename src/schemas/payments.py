from typing import Optional
from datetime import datetime, date

from pydantic import BaseModel, EmailStr, Field
from src.conf.constants import COMMENT_MAX_LENGTH, LICENSE_PLATE_MAX_LENGTH

class PaymentSchema(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    session_id: int | None
    created_at: datetime
    amount: int

    class Config:
        orm_mode = True
