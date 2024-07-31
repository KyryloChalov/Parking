import warnings

from typing import Any

from pydantic import field_validator  # , EmailStr, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

class Settings(BaseSettings):
    PG_DB: str
    PG_USER: str
    PG_PASSWORD: str
    PG_PORT: int
    PG_DOMAIN: str

    DB_URL: str
    TEST_DB_URL: str

    SECRET_KEY_JWT: str
    ALGORITHM: str

    # MAIL_USERNAME: EmailStr
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str

    REDIS_DOMAIN: str
    REDIS_PORT: int
    REDIS_PASSWORD: str | None

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # нахіба?
    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v

    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )  # noqa

    # Incompatible types in assignment (expression has type "ConfigDict", base class "BaseSettings" defined the type as "SettingsConfigDict")
    # model_config = ConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")


config = Settings()
