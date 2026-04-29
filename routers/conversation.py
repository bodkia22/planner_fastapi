from fastapi import APIRouter, Depends, HTTPException

import database
from models.conversation import Conversation
from utils.jwt import get_current_user
from schemas.conversation import ConversationRead, ConversationDetail
from sqlalchemy import select

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationRead])
def list_conversations(
    current_user=Depends(get_current_user),
    db=Depends(database.get_db),
):
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = db.execute(stmt).scalars().all()

    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db=Depends(database.get_db),
):
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    conversation = db.execute(stmt).scalar_one_or_none()
    if conversation is None:
        raise HTTPException(status_code=404)

    return conversation
