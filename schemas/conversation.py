from pydantic import BaseModel
from datetime import datetime

from typing import Literal


class MessageRead(BaseModel):
    id: int
    content: str
    role: Literal["user", "assistant"]
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationRead(BaseModel):
    id: int
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationRead):
    messages: list[MessageRead]
