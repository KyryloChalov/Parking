import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.models.models import Role
from src.conf.constants import (
    NAME_MIN_LENGTH,
    NAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
)

class UserSchema(BaseModel):
    name: str = Field(min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    username: str = Field(
        min_length=USERNAME_MIN_LENGTH, max_length=USERNAME_MAX_LENGTH
    )
    email: EmailStr
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
    
class UserUpdateSchema(BaseModel):
    name: str = Field(min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    username: str = Field(min_length=USERNAME_MIN_LENGTH, max_length=USERNAME_MAX_LENGTH)
    email: EmailStr
    updated_at: datetime = Field(default=datetime.now())
    
class UserChangeRole(BaseModel):
    role: Role
    banned: bool
    updated_at: datetime = Field(default=datetime.now())
   

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str | None
    username: str
    email: EmailStr
    avatar: str | None
    role: Role
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # noqa
    
class UserResponseAvatar(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    avatar: str | None
    role: Role

    model_config = ConfigDict(from_attributes=True)  # noqa
    
class UserChangeRoleResponse(UserResponse):
    role: Role
    banned: bool
    updated_at: datetime

class AboutUser(UserResponse):
    num_photos: int


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class UserResetPassword(BaseModel):
    password1: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
    password2: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
