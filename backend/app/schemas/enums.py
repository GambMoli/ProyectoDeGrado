from __future__ import annotations

from enum import Enum


class ProblemType(str, Enum):
    DERIVATIVE = "derivative"
    INTEGRAL = "integral"
    LIMIT = "limit"
    SIMPLIFICATION = "simplification"
    EQUATION = "equation"
    UNKNOWN = "unknown"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SourceType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


class ChatMode(str, Enum):
    AUTO = "auto"
    EXERCISE = "exercise"
    THEORY = "theory"


class MessageStatus(str, Enum):
    RECEIVED = "received"
    SOLVED = "solved"
    NEEDS_CLARIFICATION = "needs_clarification"
    ERROR = "error"


class ExerciseStatus(str, Enum):
    RECEIVED = "received"
    OCR_FAILED = "ocr_failed"
    PARSE_FAILED = "parse_failed"
    SOLVED = "solved"
    SOLVER_FAILED = "solver_failed"
