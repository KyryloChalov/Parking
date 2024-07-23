from typing import Optional
from datetime import datetime, date

from pydantic import BaseModel, EmailStr, Field
from src.conf.constants import COMMENT_MAX_LENGTH, LICENSE_PLATE_MAX_LENGTH

class BlacklistResposeSchema(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    created_at: datetime
    updated_at: datetime | None
    reason: str = Field(max_length=COMMENT_MAX_LENGTH)

class BLResposeSchema(BaseModel):
    license_plate: str
    created_at: datetime
    updated_at: datetime | None
    reason: str
    class Config:
        orm_mode = True

class BlacklistedVehicleResponse(BLResposeSchema):
    username: str
    owner_name : str | None
    owner_email: str | None

class BlacklistSchema(BaseModel):
    license_plate: str = Field(max_length=LICENSE_PLATE_MAX_LENGTH)
    reason: str = Field(max_length=COMMENT_MAX_LENGTH)

class Reminder(BaseModel):
    days : int