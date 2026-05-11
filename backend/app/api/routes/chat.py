from __future__ import annotations

from typing import Annotated, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_conversation_service, get_current_user, get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, OCRResponse
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def process_chat_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ChatResponse:
    payload.user_id = current_user.id
    return conversation_service.process_text_message(db=db, payload=payload)


@router.post(
    "/upload-exercise-image",
    response_model=OCRResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_exercise_image(
    files: Annotated[List[UploadFile], File(...)],
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> OCRResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos una imagen.",
        )
    if len(files) > 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximo 2 imagenes por solicitud.",
        )

    images: list[tuple[bytes, str, str]] = []
    for i, file in enumerate(files, start=1):
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Imagen {i}: solo se permiten archivos de imagen.",
            )
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Imagen {i}: el archivo esta vacio.",
            )
        images.append((image_bytes, file.filename or f"exercise-image-{i}", file.content_type))

    return conversation_service.extract_text_from_images(images=images)
