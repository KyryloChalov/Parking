from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionCreate(BaseModel):
    number: str

class SessionClose(BaseModel):
    number: str

class Session(BaseModel):
    id: int
    number: str
    start_time: datetime
    end_time: Optional[datetime] = None
