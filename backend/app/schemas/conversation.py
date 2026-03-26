from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.chat import MessageOut


class ConversationSummary(BaseModel):
    id: str
    user_id: str
    title: str
    summary: str | None = None
    created_at: datetime
    updated_at: datetime
    last_message_preview: str | None = None
    message_count: int

    model_config = ConfigDict(from_attributes=True)


class ConversationDetail(BaseModel):
    id: str
    user_id: str
    title: str
    summary: str | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageOut]

    model_config = ConfigDict(from_attributes=True)
