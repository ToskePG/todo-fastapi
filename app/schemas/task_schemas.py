from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class PriorityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

# ----------------------
# REQUEST / CREATE
# ----------------------
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[PriorityLevel] = PriorityLevel.medium
    assignee_id: Optional[int] = None  # samo ako task pripada grupi
    group_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[PriorityLevel] = None
    assignee_id: Optional[int] = None
    is_done: Optional[bool] = None

# ----------------------
# RESPONSE
# ----------------------
class UserInTask(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

class TaskRead(TaskBase):
    id: int
    creator: UserInTask
    assignee: Optional[UserInTask] = None
    group_id: Optional[int] = None
    is_done: bool
    created_at: datetime

    class Config:
        orm_mode = True
