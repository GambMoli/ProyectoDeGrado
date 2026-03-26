from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.enums import ChatMode, ExerciseStatus, MessageRole, MessageStatus, ProblemType, SourceType


class ChatRequest(BaseModel):
    user_id: str | None = None
    conversation_id: str | None = None
    mode: ChatMode = ChatMode.AUTO
    message: str = Field(..., min_length=2, max_length=4000)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El mensaje no puede estar vacio.")
        return cleaned


class ExerciseResolutionOut(BaseModel):
    sympy_input: str
    final_result: str
    steps: list[str]
    explanation: str
    explanation_source: str

    model_config = ConfigDict(from_attributes=True)


class ExerciseOut(BaseModel):
    id: str
    source_type: SourceType
    raw_input: str
    ocr_text: str | None = None
    detected_problem_type: ProblemType | None = None
    extracted_expression: str | None = None
    variable: str | None = None
    limit_point: str | None = None
    parse_notes: list[str] = Field(default_factory=list)
    status: ExerciseStatus
    error_message: str | None = None
    resolution: ExerciseResolutionOut | None = None

    model_config = ConfigDict(from_attributes=True)


class MessageOut(BaseModel):
    id: str
    role: MessageRole
    content: str
    source_type: SourceType | None = None
    status: MessageStatus
    error_message: str | None = None
    created_at: datetime
    exercise: ExerciseOut | None = None

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    user_id: str
    conversation_id: str
    user_message: MessageOut
    assistant_message: MessageOut
