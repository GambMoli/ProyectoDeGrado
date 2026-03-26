from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_conversation_service, get_db
from app.schemas.conversation import ConversationDetail, ConversationSummary
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(
    user_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> list[ConversationSummary]:
    return conversation_service.list_conversations(db=db, user_id=user_id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: str,
    user_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationDetail:
    return conversation_service.get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )
