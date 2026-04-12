from __future__ import annotations

from app.services.knowledge_base_service import KnowledgeSearchResult

from .models import PracticeTemplate


def build_state_from_pending(
    pending_practice: dict,
    *,
    attempts: int | None = None,
    keep_pending: bool = False,
    last_outcome: str | None = None,
) -> dict:
    history = list(pending_practice.get("practice_history") or [])
    next_state: dict = {"practice_history": history}
    if keep_pending:
        next_state["pending_practice"] = {
            **pending_practice,
            "attempts": attempts if attempts is not None else int(pending_practice.get("attempts", 0)),
        }
    else:
        next_state["last_practice_context"] = snapshot_practice_context(
            pending_practice,
            attempts=attempts,
            last_outcome=last_outcome or "completed",
        )
    return next_state


def snapshot_practice_context(
    practice_context: dict,
    *,
    attempts: int | None = None,
    last_outcome: str = "completed",
) -> dict:
    return {
        "topic": practice_context.get("topic"),
        "problem_type": practice_context.get("problem_type"),
        "raw_input": practice_context.get("raw_input"),
        "exercise_text": practice_context.get("exercise_text"),
        "expected_answer": practice_context.get("expected_answer"),
        "expected_sympy_input": practice_context.get("expected_sympy_input"),
        "hint": practice_context.get("hint"),
        "grading_mode": practice_context.get("grading_mode"),
        "rubric": practice_context.get("rubric"),
        "reference_summary": practice_context.get("reference_summary"),
        "keywords": list(practice_context.get("keywords") or []),
        "attempts": attempts if attempts is not None else int(practice_context.get("attempts", 0)),
        "practice_history": list(practice_context.get("practice_history") or []),
        "status": "completed",
        "last_outcome": last_outcome,
    }


def get_practice_history(current_state: dict, *, history_limit: int) -> list[dict]:
    history = list((current_state or {}).get("practice_history") or [])
    cleaned_history: list[dict] = []
    for entry in history[-history_limit:]:
        if isinstance(entry, dict):
            cleaned_history.append(
                {
                    "topic": str(entry.get("topic", "")).strip(),
                    "signature": str(entry.get("signature", "")).strip(),
                    "exercise_text": str(entry.get("exercise_text", "")).strip(),
                }
            )
    return cleaned_history


def build_updated_history(
    *,
    current_state: dict,
    template: PracticeTemplate,
    history_limit: int,
) -> list[dict]:
    history = get_practice_history(current_state, history_limit=history_limit)
    signature_source = template.raw_input or template.expected_sympy_input or template.exercise_text
    history.append(
        {
            "topic": template.topic,
            "signature": signature_source.strip(),
            "exercise_text": template.exercise_text.strip(),
        }
    )
    return history[-history_limit:]


def format_reference_context(references: list[KnowledgeSearchResult]) -> str:
    if not references:
        return "Sin referencias del corpus."

    blocks = []
    for index, reference in enumerate(references[:4], start=1):
        doc = reference.document
        blocks.append(
            f"[{index}] curso={doc.course}; unidad={doc.unit}; tema={doc.topic}; "
            f"subtema={doc.subtopic}; texto={doc.text}"
        )
    return "\n".join(blocks)


def format_history_block(history: list[dict]) -> str:
    if not history:
        return "No hay historial previo."
    lines = []
    for entry in history[-4:]:
        topic = entry.get("topic", "")
        signature = entry.get("signature", "")
        lines.append(f"- {topic}: {signature}")
    return "\n".join(lines)


def compact_practice_context(practice_context: dict) -> dict:
    if not practice_context:
        return {}
    return {
        "topic": practice_context.get("topic"),
        "problem_type": practice_context.get("problem_type"),
        "exercise_text": practice_context.get("exercise_text"),
        "last_outcome": practice_context.get("last_outcome"),
        "status": practice_context.get("status"),
    }


def reference_summary(references: list[KnowledgeSearchResult]) -> str | None:
    if not references:
        return None
    return " ".join(reference.document.text for reference in references[:2]).strip()


def keywords_from_references(references: list[KnowledgeSearchResult]) -> list[str]:
    keywords: list[str] = []
    for reference in references:
        keywords.extend(reference.document.tags)
    seen: set[str] = set()
    deduped: list[str] = []
    for keyword in keywords:
        if keyword in seen:
            continue
        seen.add(keyword)
        deduped.append(keyword)
    return deduped[:6]


def history_topic_count(history: list[dict], topic: str) -> int:
    return sum(1 for entry in history if str(entry.get("topic", "")).strip() == topic)
