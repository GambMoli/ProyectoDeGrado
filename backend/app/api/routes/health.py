from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_conversation_service, get_db, get_settings_dependency
from app.core.config import Settings
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.get("/health")
def healthcheck(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dependency),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> dict[str, str | bool | int]:
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "up",
        "ocr_provider": settings.ocr_provider,
        "ollama_enabled": settings.ollama_enabled,
        "knowledge_documents": conversation_service.count_knowledge_documents(),
    }
