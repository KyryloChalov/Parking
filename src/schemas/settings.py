from pydantic import BaseModel


class SettingCreateSchema(BaseModel):
    capacity: int
    num_days_reminder: int | None = None
    num_days_benefit: int | None = None


class SettingResponseSchema(BaseModel):
    id: int
    capacity: int
    num_days_reminder: int | None
    num_days_benefit: int | None

    class Config:
        from_attributes = True


class SettingUpdateSchema(BaseModel):
    capacity: int
    num_days_reminder: int | None = None
    num_days_benefit: int | None = None
