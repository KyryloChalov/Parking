import re
import uuid
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator
from typing import Optional, List

from src.conf.constants import RATING_MIN_VALUE, RATING_MAX_VALUE
from src.conf.messages import RATING_VALUE_INCORRECT


class RatingSchema(BaseModel):
    rating: int = Field(ge=1, le=5)

    @validator("rating")
    def rating_number(cls, rating_num):
        if (rating_num < RATING_MIN_VALUE) or (rating_num > RATING_MAX_VALUE):
            raise ValueError(RATING_VALUE_INCORRECT)
        return rating_num


class RatingBaseResponseSchema(BaseModel):
    id: int
    user_id: uuid.UUID
    photo_id: int


class RatingResponseSchema(RatingBaseResponseSchema):
    rating: int = Field(ge=1, le=5)


class RatingAVGResponseSchema(BaseModel):
    photo_id: int
    rating: float = Field(ge=1, le=5)


class PhotosSchema(BaseModel):
    id: int = 1
    path: str
    description: str
    created_at: Optional[datetime]
    path_transform: str
    user_id: uuid.UUID
    updated_at: Optional[datetime] = Field(None)
    
class PhotosResponse(BaseModel):
    id: int = 1
    path: str
    description: str
    created_at: Optional[datetime]
    path_transform: Optional[str]
    user_id: uuid.UUID
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)  # noqa
