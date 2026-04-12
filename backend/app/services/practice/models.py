from __future__ import annotations

from dataclasses import dataclass

from app.services.knowledge_base_service import KnowledgeSearchResult


@dataclass(slots=True)
class PracticeGenerationResult:
    text: str
    state: dict
    exercise_text: str
    hint: str
    topic: str
    problem_type: str


@dataclass(slots=True)
class PracticeGradeResult:
    text: str
    is_correct: bool
    next_state: dict


@dataclass(slots=True)
class PracticeTemplate:
    topic: str
    problem_type: str
    exercise_text: str
    hint: str
    grading_mode: str = "symbolic"
    raw_input: str | None = None
    expected_answer: str | None = None
    expected_sympy_input: str | None = None
    rubric: str | None = None
    reference_summary: str | None = None
    keywords: list[str] | None = None


@dataclass(slots=True)
class PracticeStrategy:
    topic: str
    generator_mode: str
    references: list[KnowledgeSearchResult]
