from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from app.schemas.enums import ChatMode
from app.services.knowledge_base_service import KnowledgeBaseService, normalize_search_text
from app.services.math_parser_service import MathParserService
from app.services.ollama_client import OllamaClient, OllamaClientError
from app.utils.expression_normalizer import looks_like_structured_math

if TYPE_CHECKING:
    from app.core.config import Settings

PlanAction = Literal[
    "answer_theory",
    "solve_exercise",
    "generate_practice",
    "grade_practice",
    "ask_clarification",
]

DetailLevel = Literal["auto", "brief", "detailed"]


@dataclass(slots=True)
class ConversationPlan:
    actions: list[PlanAction]
    reason: str
    topic: str | None = None
    detail_level: DetailLevel = "auto"


class ConversationPlannerService:
    _practice_request_nouns = (
        "ejercicio",
        "ejercicios",
        "practica",
        "practicar",
        "simulacro",
        "simulacros",
        "examen",
        "pregunta",
        "preguntas",
    )
    _practice_request_verbs = (
        "dame",
        "darme",
        "ponme",
        "proponme",
        "quiero",
        "necesito",
        "puedes",
        "podrias",
        "podria",
        "genera",
        "generame",
        "mandame",
        "regalame",
        "intentarlo",
    )
    _theory_patterns = (
        "explicame",
        "que es",
        "que sabes",
        "como funciona",
        "para que sirve",
        "tema",
        "concepto",
        "resumen",
        "repaso",
    )
    _detail_patterns = {
        "brief": ("breve", "corto", "resumido", "rapido"),
        "detailed": ("detallado", "paso a paso", "profundo", "con detalle"),
    }
    _explicit_answer_markers = (
        "resultado",
        "respuesta",
        "creo que",
        "me dio",
        "seria",
        "mi resultado",
        "mi respuesta",
    )
    _practice_correction_patterns = (
        "no de",
        "no era",
        "eso es de",
        "eso era de",
        "te pedi",
        "repito",
    )
    _topic_aliases = (
        ("serie_de_taylor", ("serie de taylor", "taylor")),
        ("newton_raphson", ("newton raphson", "newton-raphson")),
        ("regula_falsi", ("regula falsi", "falsa posicion")),
        ("metodo_de_la_secante", ("metodo de la secante", "secante")),
        ("punto_fijo", ("punto fijo",)),
        ("biseccion", ("biseccion",)),
        ("lagrange", ("lagrange",)),
        ("interpolacion_newton", ("interpolacion de newton",)),
        ("simpson_1_3", ("simpson 1/3", "simpson 1 3", "simpson un tercio")),
        ("trapecios", ("trapecio", "trapecios")),
        ("derivative", ("derivad",)),
        ("integral", ("integral",)),
        ("limit", ("limite", "lim ")),
        ("equation", ("ecuacion",)),
    )
    _token_pattern = re.compile(r"[a-z0-9]+")
    _allowed_actions: tuple[PlanAction, ...] = (
        "answer_theory",
        "solve_exercise",
        "generate_practice",
        "grade_practice",
        "ask_clarification",
    )

    def __init__(
        self,
        *,
        settings: Settings,
        knowledge_base_service: KnowledgeBaseService,
        parser_service: MathParserService,
        ollama_client: OllamaClient | None = None,
    ) -> None:
        self.settings = settings
        self.knowledge_base_service = knowledge_base_service
        self.parser_service = parser_service
        self.ollama_client = ollama_client

    def plan(
        self,
        *,
        message: str,
        requested_mode: ChatMode,
        conversation_context: list[str],
        agent_state: dict | None,
    ) -> ConversationPlan:
        if requested_mode == ChatMode.THEORY:
            return ConversationPlan(
                actions=["answer_theory"],
                reason="requested_mode_theory",
                topic=self._detect_topic(normalize_search_text(message)),
                detail_level=self._detect_detail_level(normalize_search_text(message)),
            )

        if requested_mode == ChatMode.EXERCISE:
            return ConversationPlan(
                actions=["solve_exercise"],
                reason="requested_mode_exercise",
                topic=self._detect_topic(normalize_search_text(message)),
                detail_level=self._detect_detail_level(normalize_search_text(message)),
            )

        state = agent_state or {}
        planned = self._plan_with_ollama(
            message=message,
            conversation_context=conversation_context,
            agent_state=state,
        )
        if planned:
            return self._apply_guardrails(
                plan=planned,
                message=message,
                agent_state=state,
            )
        return self._plan_with_rules(message=message, agent_state=state)

    def _plan_with_ollama(
        self,
        *,
        message: str,
        conversation_context: list[str],
        agent_state: dict,
    ) -> ConversationPlan | None:
        if not self.ollama_client:
            return None

        history = "\n".join(conversation_context) if conversation_context else "Sin contexto previo relevante."
        prompt = f"""
Eres el planner interno de un tutor matematico universitario.

Mensaje actual:
{message}

Contexto reciente:
{history}

Estado pedagogico actual:
{json.dumps(agent_state, ensure_ascii=False)}

Debes decidir que herramientas conviene usar antes de responder.
Puedes devolver una o varias acciones, en el orden en que deban ejecutarse.

Acciones permitidas:
- answer_theory
- solve_exercise
- generate_practice
- grade_practice
- ask_clarification

Reglas de planificacion:
- Una practica pendiente es contexto, no una carcel. Si el estudiante cambia de tema, sigue la nueva intencion.
- Usa grade_practice solo cuando el mensaje parezca realmente un intento de respuesta al ejercicio pendiente.
- Si el mensaje mezcla explicacion y practica, devuelve ["answer_theory","generate_practice"].
- Si el mensaje pide solo practica, incluso de forma indirecta o coloquial, devuelve ["generate_practice"].
- Si el mensaje pide resolver un ejercicio concreto o comparte una expresion para trabajarla, devuelve ["solve_exercise"].
- Si el mensaje pide teoria, definiciones, comparaciones o repaso, incluye ["answer_theory"].
- Si falta informacion importante, usa ["ask_clarification"].

Ejemplos:
- "Asi esta bien, podrias darme un ejercicio de calculo 2" -> {{"actions":["generate_practice"],"reason":"course_level_practice","topic":"calculo_2","detail_level":"auto"}}
- "Dime que sabes de derivadas y proponme un ejercicio" -> {{"actions":["answer_theory","generate_practice"],"reason":"mixed_theory_practice","topic":"derivative","detail_level":"auto"}}
- Si hay una practica de derivadas pendiente y el estudiante dice "6x+2" -> {{"actions":["grade_practice"],"reason":"practice_attempt","topic":"derivative","detail_level":"auto"}}
- Si hay una practica pendiente y el estudiante escribe "Resuelve x^2 + 3*x = 10" -> {{"actions":["solve_exercise"],"reason":"new_math_task","topic":"equation","detail_level":"auto"}}

Tambien devuelve:
- reason: una etiqueta corta
- topic: el tema detectado si existe
- detail_level: "brief", "detailed" o "auto"

Devuelve solo JSON valido con esta forma:
{{"actions":["answer_theory","generate_practice"],"reason":"mixed_theory_practice","topic":"derivative","detail_level":"auto"}}
""".strip()
        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un planner interno. Devuelves solo JSON valido.",
                prompt=prompt,
            )
            payload = self._extract_json(raw)
        except (OllamaClientError, ValueError, json.JSONDecodeError):
            return None

        actions = self._normalize_actions(payload.get("actions"))
        if not actions:
            return None

        detail_level = self._normalize_detail_level(payload.get("detail_level"))
        topic = payload.get("topic")
        if topic is not None:
            topic = str(topic)

        return ConversationPlan(
            actions=actions,
            reason=str(payload.get("reason") or "llm_planner"),
            topic=topic,
            detail_level=detail_level,
        )

    def _plan_with_rules(
        self,
        *,
        message: str,
        agent_state: dict,
    ) -> ConversationPlan:
        normalized = normalize_search_text(message)
        pending_practice = agent_state.get("pending_practice")
        detected_topic = self._detect_topic(normalized)

        if pending_practice and self._looks_like_practice_correction(
            normalized_message=normalized,
            pending_topic=str(pending_practice.get("topic") or ""),
            detected_topic=detected_topic,
        ):
            return ConversationPlan(
                actions=["generate_practice"],
                reason="rule_practice_topic_correction",
                topic=detected_topic,
                detail_level=self._detect_detail_level(normalized),
            )

        if self._looks_like_mixed_theory_practice_request(normalized):
            return ConversationPlan(
                actions=["answer_theory", "generate_practice"],
                reason="rule_mixed_theory_practice",
                topic=detected_topic,
                detail_level=self._detect_detail_level(normalized),
            )

        if pending_practice and self._looks_like_practice_attempt(
            normalized_message=normalized,
            pending_practice=pending_practice,
        ):
            return ConversationPlan(
                actions=["grade_practice"],
                reason="rule_pending_practice_answer",
                topic=str(pending_practice.get("topic") or ""),
                detail_level=self._detect_detail_level(normalized),
            )

        if self._looks_like_practice_request(normalized):
            return ConversationPlan(
                actions=["generate_practice"],
                reason="rule_practice_request",
                topic=detected_topic,
                detail_level=self._detect_detail_level(normalized),
            )

        if self._looks_like_theory_query(normalized):
            return ConversationPlan(
                actions=["answer_theory"],
                reason="rule_theory_query",
                topic=detected_topic,
                detail_level=self._detect_detail_level(normalized),
            )

        try:
            self.parser_service.parse(message)
            return ConversationPlan(
                actions=["solve_exercise"],
                reason="rule_parser_detected_exercise",
                topic=detected_topic,
                detail_level=self._detect_detail_level(normalized),
            )
        except Exception:
            if self._has_curricular_grounding(message=message, normalized_message=normalized):
                return ConversationPlan(
                    actions=["answer_theory"],
                    reason="rule_curricular_grounding",
                    topic=detected_topic or self.knowledge_base_service.detect_course_hint(message),
                    detail_level=self._detect_detail_level(normalized),
                )
            return ConversationPlan(
                actions=["ask_clarification"],
                reason="rule_clarification",
                topic=detected_topic,
                detail_level=self._detect_detail_level(normalized),
            )

    def _apply_guardrails(
        self,
        *,
        plan: ConversationPlan,
        message: str,
        agent_state: dict,
    ) -> ConversationPlan:
        normalized = normalize_search_text(message)
        pending_practice = agent_state.get("pending_practice")
        detected_topic = self._detect_topic(normalized)
        detail_level = plan.detail_level

        if pending_practice and self._looks_like_practice_correction(
            normalized_message=normalized,
            pending_topic=str(pending_practice.get("topic") or ""),
            detected_topic=detected_topic,
        ):
            return ConversationPlan(
                actions=["generate_practice"],
                reason="guardrail_practice_topic_correction",
                topic=detected_topic,
                detail_level=detail_level,
            )

        if self._looks_like_mixed_theory_practice_request(normalized):
            return ConversationPlan(
                actions=["answer_theory", "generate_practice"],
                reason="guardrail_mixed_theory_practice",
                topic=detected_topic,
                detail_level=detail_level,
            )

        if plan.actions == ["solve_exercise"] and self._looks_like_practice_request(normalized):
            if not self._contains_explicit_math_task(message):
                return ConversationPlan(
                    actions=["generate_practice"],
                    reason="guardrail_reroute_natural_practice_request",
                    topic=detected_topic,
                    detail_level=detail_level,
                )

        if plan.actions == ["ask_clarification"] and self._looks_like_practice_request(normalized):
            return ConversationPlan(
                actions=["generate_practice"],
                reason="guardrail_reroute_practice_request",
                topic=detected_topic,
                detail_level=detail_level,
            )

        if plan.actions == ["ask_clarification"] and self._has_curricular_grounding(
            message=message,
            normalized_message=normalized,
        ):
            return ConversationPlan(
                actions=["answer_theory"],
                reason="guardrail_reroute_curricular_grounding",
                topic=detected_topic or self.knowledge_base_service.detect_course_hint(message),
                detail_level=detail_level,
            )

        if pending_practice and self._looks_like_practice_attempt(
            normalized_message=normalized,
            pending_practice=pending_practice,
        ):
            return ConversationPlan(
                actions=["grade_practice"],
                reason="guardrail_pending_practice",
                topic=str(pending_practice.get("topic") or ""),
                detail_level=detail_level,
            )

        if pending_practice and self._looks_like_theory_query(normalized):
            return ConversationPlan(
                actions=["answer_theory"],
                reason="guardrail_context_switch_theory",
                topic=detected_topic,
                detail_level=detail_level,
            )

        if pending_practice and self._looks_like_new_math_task(
            message=message,
            normalized_message=normalized,
            pending_practice=pending_practice,
        ):
            return ConversationPlan(
                actions=["solve_exercise"],
                reason="guardrail_context_switch_new_math",
                topic=detected_topic,
                detail_level=detail_level,
            )

        return plan

    @classmethod
    def _extract_json(cls, raw: str) -> dict:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in planner response.")
        return json.loads(match.group(0))

    def _normalize_actions(self, raw_actions: object) -> list[PlanAction]:
        if not isinstance(raw_actions, list):
            return []

        normalized: list[PlanAction] = []
        for raw_action in raw_actions:
            if raw_action not in self._allowed_actions:
                continue
            action = raw_action
            if action not in normalized:
                normalized.append(action)
        return normalized

    @staticmethod
    def _normalize_detail_level(raw_value: object) -> DetailLevel:
        if raw_value in {"brief", "detailed", "auto"}:
            return raw_value
        return "auto"

    @classmethod
    def _looks_like_mixed_theory_practice_request(cls, normalized_message: str) -> bool:
        return cls._looks_like_theory_query(normalized_message) and cls._looks_like_practice_request(
            normalized_message
        )

    @classmethod
    def _looks_like_practice_request(cls, normalized_message: str) -> bool:
        tokens = cls._math_tokens(normalized_message)
        noun_hits = tokens.intersection(cls._practice_request_nouns)
        verb_hits = tokens.intersection(cls._practice_request_verbs)
        return bool(noun_hits) and (bool(verb_hits) or len(noun_hits) >= 2)

    @classmethod
    def _looks_like_theory_query(cls, normalized_message: str) -> bool:
        return any(pattern in normalized_message for pattern in cls._theory_patterns)

    @classmethod
    def _looks_like_practice_attempt(
        cls,
        *,
        normalized_message: str,
        pending_practice: dict,
    ) -> bool:
        if cls._looks_like_theory_query(normalized_message):
            return False

        if cls._looks_like_practice_request(normalized_message):
            return False

        if any(marker in normalized_message for marker in cls._explicit_answer_markers):
            return True

        expected_answer = str(pending_practice.get("expected_answer") or "")
        student_tokens = cls._math_tokens(normalized_message)
        expected_tokens = cls._math_tokens(expected_answer)
        if not student_tokens or not expected_tokens:
            return False

        overlap = len(student_tokens.intersection(expected_tokens))
        student_overlap = overlap / len(student_tokens)
        expected_overlap = overlap / len(expected_tokens)
        return student_overlap >= 0.75 and expected_overlap >= 0.5

    def _looks_like_new_math_task(
        self,
        *,
        message: str,
        normalized_message: str,
        pending_practice: dict,
    ) -> bool:
        if self._looks_like_practice_attempt(
            normalized_message=normalized_message,
            pending_practice=pending_practice,
        ):
            return False

        if self._looks_like_theory_query(normalized_message):
            return False

        try:
            self.parser_service.parse(message)
            return True
        except Exception:
            return False

    @classmethod
    def _looks_like_practice_correction(
        cls,
        *,
        normalized_message: str,
        pending_topic: str,
        detected_topic: str | None,
    ) -> bool:
        if not detected_topic or detected_topic == pending_topic:
            return False
        return any(pattern in normalized_message for pattern in cls._practice_correction_patterns)

    @staticmethod
    def _contains_explicit_math_task(message: str) -> bool:
        normalized = normalize_search_text(message)
        if any(token in normalized for token in ("resuelve", "calcula", "simplifica", "evalua")):
            return True
        return looks_like_structured_math(message)

    def _detect_topic(self, normalized_message: str) -> str | None:
        for topic, aliases in self._topic_aliases:
            if any(alias in normalized_message for alias in aliases):
                return topic

        matches = self.knowledge_base_service.search(normalized_message, limit=1)
        if matches:
            return matches[0].document.topic
        return None

    def _has_curricular_grounding(self, *, message: str, normalized_message: str) -> bool:
        if self.knowledge_base_service.detect_course_hint(message):
            return True

        if self._detect_topic(normalized_message):
            return True

        return bool(self.knowledge_base_service.search(message, limit=1))

    @classmethod
    def _detect_detail_level(cls, normalized_message: str) -> DetailLevel:
        for detail_level, markers in cls._detail_patterns.items():
            if any(marker in normalized_message for marker in markers):
                return detail_level  # type: ignore[return-value]
        return "auto"

    @classmethod
    def _math_tokens(cls, value: str) -> set[str]:
        normalized = normalize_search_text(value)
        return {
            token
            for token in cls._token_pattern.findall(normalized)
            if token not in {"el", "la", "de", "es", "mi", "resultado", "respuesta"}
        }
