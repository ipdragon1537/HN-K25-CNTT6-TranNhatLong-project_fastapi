from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
class EventCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class EventUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime


class MemberAdd(BaseModel):
    user_id: int
class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    role: str
    joined_at: datetime