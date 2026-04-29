from typing import Literal
from pydantic import BaseModel


class AssistantResponse(BaseModel):
    message: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AssistantRequest(BaseModel):
    messages: list[ChatMessage]


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    content: str


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
