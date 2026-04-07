from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Task(BaseModel):
    id: int
    title: str
    description: str
    is_done: bool = False
    created_at: datetime
    priority: int = 0


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: Optional[int] = 0


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_done: Optional[bool] = None
    priority: Optional[int] = None
