from pydantic import BaseModel,Field
class EventCreate(BaseModel):
    name:str = Field(min_length=1,max_length=255)
    description:str | None = None
class EventUpdate(BaseModel):
    name:str | None = Field(default=None,min_length=1,max_length=255)
    description:str | None = None
class AddMember(BaseModel):
    user_id:int
class EventResponse(BaseModel):
    id:int
    name:str
    description:str | None
    owner_id:int
    