"""скопіював з contacts"""

import re
import uuid
from typing import Optional, List
from datetime import datetime, date

from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator


class RatingSchema(BaseModel):
    rating: int = Field(ge=1, le=5)

    @validator("rating")
    def rating_number(cls, rating_num):
        if (rating_num < 1) or (rating_num > 5):
            raise ValueError("Rating must be between 1 and 5")
        return rating_num


class ContactSchema(BaseModel):
    name: str = Field(max_length=30)
    surname: str = Field(max_length=30)
    email: EmailStr = Field(max_length=80)
    birthday: Optional[date] = Field(None)
    phone: Optional[str] = Field(max_length=20)
    info: Optional[str] = Field(max_length=200, default=None)

    @validator("phone")
    def phone_number(cls, phone_num):
        match = re.match(r"\d{12}", phone_num)
        if (match is None) or (len(phone_num) != 12):
            print(match, len(phone_num), phone_num)
            raise ValueError("Phone number must have 12 digits")
        return phone_num


class ContactUpdateSchema(ContactSchema):
    created_at: datetime = Field(default=datetime.now())


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    surname: str
    email: EmailStr
    birthday: date
    phone: str
    info: str | None

    model_config = ConfigDict(from_attributes=True)  # noqa


class ImagesSchema(BaseModel):
    id: int = 1
    path: str
    description: str
    created_at: Optional[date]
    path_transform: str
    user_id: uuid.UUID
    updated_at: Optional[date] = Field(None)
