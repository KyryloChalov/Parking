from typing import Optional
from datetime import datetime, date

from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator
from src.conf.constants import COMMENT_MIN_LENGTH, COMMENT_MAX_LENGTH

import uuid


class CommentSchema(BaseModel):
    opinion: str = Field(min_length=COMMENT_MIN_LENGTH, max_length=COMMENT_MAX_LENGTH)


class CommentResposeSchema(BaseModel):
    id: int
    opinion: str = Field(min_length=COMMENT_MIN_LENGTH, max_length=COMMENT_MAX_LENGTH)
    user_id: uuid.UUID
    photo_id: int


class CommentUpdateSchema(BaseModel):
    opinion: str = Field(min_length=COMMENT_MIN_LENGTH, max_length=COMMENT_MAX_LENGTH)
