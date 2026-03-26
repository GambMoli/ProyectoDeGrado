from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_conversation_service, get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def process_chat_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ChatResponse:
    return conversation_service.process_text_message(db=db, payload=payload)


@router.post(
    "/upload-exercise-image",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_exercise_image(
    file: UploadFile = File(...),
    user_id: str | None = Form(default=None),
    conversation_id: str | None = Form(default=None),
    prompt: str | None = Form(default=None),
    db: Session = Depends(get_db),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ChatResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos de imagen.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen esta vacia.",
        )

    return conversation_service.process_image_message(
        db=db,
        image_bytes=image_bytes,
        filename=file.filename or "exercise-image",
        content_type=file.content_type,
        user_id=user_id,
        conversation_id=conversation_id,
        prompt=prompt,
    )
