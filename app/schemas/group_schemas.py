from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ✅ Schemas za response i request
class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None

class UserInGroup(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

class GroupRead(GroupBase):
    id: int
    admin_id: int
    members: List[UserInGroup]

    class Config:
        from_attributes = True
