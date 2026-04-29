from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, func

from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

if TYPE_CHECKING:
    from models.conversation import Conversation


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    content: Mapped[str] = mapped_column(String(1000))
    role: Mapped[str] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
