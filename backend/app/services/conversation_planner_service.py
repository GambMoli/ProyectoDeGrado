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
    "explain_practice_context",
    "grade_practice",
    "ask_clarification",
]

DetailLevel = Literal["auto", "brief", "detailed"]
PlannerIntent = Literal[
    "theory_request",
    "practice_request",
    "mixed_theory_practice",
    "solve_new_problem",
    "grade_active_practice",
    "explain_practice_context",
    "clarify",
]
PlannerTarget = Literal[
    "active_practice",
    "recent_practice",
    "new_problem",
    "new_topic",
    "general_curriculum",
    "unknown",
]


@dataclass(slots=True)
class ConversationPlan:
    actions: list[PlanAction]
    reason: str
    topic: str | None = None
    detail_level: DetailLevel = "auto"


@dataclass(slots=True)
class SemanticPlannerDecision:
    intent: PlannerIntent
    target: PlannerTarget
    reason: str
    confidence: float
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
    _pending_explanation_markers = (
        "explicame",
        "explicarme",
        "explicar",
        "paso a paso",
        "paso por paso",
        "procedimiento",
        "como se hace",
        "como seria",
        "guiame",
        "desarrolla",
    )
    _pending_reference_markers = (
        "ese ejercicio",
        "este ejercicio",
        "el ejercicio",
        "esa integral",
        "esta integral",
        "esa derivada",
        "esta derivada",
        "ese limite",
        "este limite",
        "esa ecuacion",
        "esta ecuacion",
        "ese problema",
        "este problema",
        "la solucion",
        "la respuesta",
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
        "explain_practice_context",
        "grade_practice",
        "ask_clarification",
    )
    _allowed_intents: tuple[PlannerIntent, ...] = (
        "theory_request",
        "practice_request",
        "mixed_theory_practice",
        "solve_new_problem",
        "grade_active_practice",
        "explain_practice_context",
        "clarify",
    )
    _allowed_targets: tuple[PlannerTarget, ...] = (
        "active_practice",
        "recent_practice",
        "new_problem",
        "new_topic",
        "general_curriculum",
        "unknown",
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
        contextual_plan = self._plan_from_existing_practice_context(
            message=message,
            conversation_context=conversation_context,
            agent_state=state,
        )
        if contextual_plan:
            return contextual_plan

        planned = self._plan_with_ollama(
            message=message,
            conversation_context=conversation_context,
            agent_state=state,
        )
        if planned:
            plan = self._apply_guardrails(
                plan=planned,
                message=message,
                agent_state=state,
            )
            recovered = self._recover_practice_follow_up_with_ollama(
                current_plan=plan,
                message=message,
                conversation_context=conversation_context,
                agent_state=state,
            )
            if recovered:
                return recovered
            return plan
        return self._plan_with_rules(message=message, agent_state=state)

    def _plan_from_existing_practice_context(
        self,
        *,
        message: str,
        conversation_context: list[str],
        agent_state: dict,
    ) -> ConversationPlan | None:
        if not self.ollama_client or not self._has_practice_context(agent_state):
            return None

        history = "\n".join(conversation_context) if conversation_context else "Sin contexto previo relevante."
        prompt = f"""
Eres un resolutor semantico del contexto de practica de un tutor matematico.

Hay una practica activa o reciente en la conversacion. Tu trabajo es decidir si el mensaje actual:
- continua ese mismo ejercicio para explicarlo,
- entrega un intento de respuesta,
- abre una pregunta teorica,
- pide otra practica,
- o trae un problema nuevo.

Mensaje actual:
{message}

Contexto reciente:
{history}

Estado pedagogico:
{json.dumps(agent_state, ensure_ascii=False)}

Si el estudiante esta pidiendo ayuda, desarrollo, guia o procedimiento del ejercicio activo o reciente, devuelve explain_practice_context.
Si esta entregando una respuesta al ejercicio activo, devuelve grade_practice.
Si cambia claramente de objetivo, devuelve answer_theory, generate_practice o solve_exercise segun corresponda.
No te bases en palabras exactas: usa la continuidad conversacional y el estado.

Devuelve solo JSON valido:
{{
  "actions":["explain_practice_context"],
  "reason":"continues current exercise",
  "topic":"integral",
  "detail_level":"detailed",
  "confidence":0.91
}}
""".strip()

        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un planner interno. Devuelves solo JSON valido.",
                prompt=prompt,
                temperature=0.1,
            )
            payload = self._extract_json(raw)
        except (OllamaClientError, ValueError, json.JSONDecodeError):
            return None

        actions = self._normalize_actions(payload.get("actions"))
        if not actions:
            return None

        confidence = self._normalize_confidence(payload.get("confidence"))
        if confidence < 0.6:
            return None

        return ConversationPlan(
            actions=actions,
            reason=f"contextual_practice_{payload.get('reason') or 'semantic'}",
            topic=str(payload.get("topic")) if payload.get("topic") is not None else None,
            detail_level=self._normalize_detail_level(payload.get("detail_level")),
        )

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
        prompt = self._build_semantic_prompt(
            message=message,
            conversation_history=history,
            agent_state=agent_state,
        )
        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un planner interno. Devuelves solo JSON valido.",
                prompt=prompt,
                temperature=0.1,
            )
            payload = self._extract_json(raw)
        except (OllamaClientError, ValueError, json.JSONDecodeError):
            return None

        actions = self._normalize_actions(payload.get("actions"))
        if not actions:
            semantic_plan = self._plan_from_semantic_payload(payload)
            if semantic_plan:
                return semantic_plan
            return None

        detail_level = self._normalize_detail_level(payload.get("detail_level"))
        topic = payload.get("topic")
        if topic is not None:
            topic = str(topic)

        return ConversationPlan(
            actions=actions,
            reason=str(payload.get("reason") or "llm_planner_legacy"),
            topic=topic,
            detail_level=detail_level,
        )

    def _build_semantic_prompt(
        self,
        *,
        message: str,
        conversation_history: str,
        agent_state: dict,
    ) -> str:
        active_practice_summary = self._practice_context_summary(agent_state, "pending_practice")
        recent_practice_summary = self._practice_context_summary(agent_state, "last_practice_context")
        return f"""
Eres el planner interno de un tutor matematico universitario.

Tu trabajo es inferir la intencion semantica del estudiante, no reaccionar a palabras exactas.
Debes usar el mensaje actual, el contexto reciente y el estado pedagogico para decidir que quiere hacer el estudiante.

Mensaje actual:
{message}

Contexto reciente:
{conversation_history}

Estado pedagogico actual:
{json.dumps(agent_state, ensure_ascii=False)}

Contexto de practica activa:
{active_practice_summary}

Contexto de practica reciente:
{recent_practice_summary}

Clasifica el mensaje en una sola intencion principal:
- theory_request
- practice_request
- mixed_theory_practice
- solve_new_problem
- grade_active_practice
- explain_practice_context
- clarify

Y en un objetivo principal:
- active_practice
- recent_practice
- new_problem
- new_topic
- general_curriculum
- unknown

Guia semantica:
- Si el estudiante quiere que le propongan un ejercicio, la intencion es practice_request aunque no use palabras exactas.
- Si quiere que le expliques el ejercicio activo o el ejercicio que acaban de resolver/corregir, la intencion es explain_practice_context.
- Si parece que esta entregando su resultado al ejercicio activo, la intencion es grade_active_practice.
- Si trae un problema nuevo concreto para resolver, la intencion es solve_new_problem.
- Si pregunta teoria o contenido, la intencion es theory_request.
- Si mezcla repaso y practica, usa mixed_theory_practice.
- Si el tutor acaba de ofrecer explicar el mismo ejercicio y el estudiante acepta o pide seguir, eso sigue siendo explain_practice_context aunque el mensaje sea corto.
- Usa clarify solo si de verdad no puedes inferir el objetivo.

Ejemplos:
- "Dame un ejercicio de integrales" -> {{"intent":"practice_request","target":"new_topic","topic":"integral","detail_level":"auto","confidence":0.93,"reason":"wants a new practice exercise"}}
- "Puedes explicarme ese ejercicio paso por paso?" con practica activa -> {{"intent":"explain_practice_context","target":"active_practice","topic":"integral","detail_level":"detailed","confidence":0.95,"reason":"asks to walk through the active exercise"}}
- "No supe resolverlo, podrias hacerme el paso por paso?" con practica activa -> {{"intent":"explain_practice_context","target":"active_practice","topic":"derivative","detail_level":"detailed","confidence":0.94,"reason":"needs guided walkthrough of the current exercise"}}
- "Si, dame el paso a paso" despues de que el tutor ofrecio explicarlo y ya no hay practica activa -> {{"intent":"explain_practice_context","target":"recent_practice","topic":"integral","detail_level":"detailed","confidence":0.93,"reason":"accepts walkthrough of the recently completed exercise"}}
- "El ejercicio anterior no lo supe resolver, dame el paso por paso." -> {{"intent":"explain_practice_context","target":"recent_practice","topic":"derivative","detail_level":"detailed","confidence":0.92,"reason":"asks to revisit the previous exercise"}}
- "x^3/3 + 2x^2 + x + C" con practica activa -> {{"intent":"grade_active_practice","target":"active_practice","topic":"integral","detail_level":"auto","confidence":0.88,"reason":"looks like an answer attempt"}}
- "Resuelve la integral de x^2 + 1 dx" -> {{"intent":"solve_new_problem","target":"new_problem","topic":"integral","detail_level":"detailed","confidence":0.97,"reason":"explicit new math problem"}}
- "Que sabes de derivadas y proponme un ejercicio" -> {{"intent":"mixed_theory_practice","target":"new_topic","topic":"derivative","detail_level":"auto","confidence":0.96,"reason":"asks for explanation plus practice"}}

Devuelve solo JSON valido con esta forma:
{{
  "intent":"practice_request",
  "target":"new_topic",
  "topic":"integral",
  "detail_level":"auto",
  "confidence":0.93,
  "reason":"..."
}}
""".strip()

    def _recover_practice_follow_up_with_ollama(
        self,
        *,
        current_plan: ConversationPlan,
        message: str,
        conversation_context: list[str],
        agent_state: dict,
    ) -> ConversationPlan | None:
        normalized_message = normalize_search_text(message)
        if not self.ollama_client or current_plan.actions not in (
            ["ask_clarification"],
            ["answer_theory"],
            ["generate_practice"],
            ["solve_exercise"],
        ):
            return None

        if not self._has_practice_context(agent_state):
            return None

        if current_plan.actions == ["answer_theory"] and self._looks_like_theory_query(normalized_message):
            return None

        history = "\n".join(conversation_context) if conversation_context else "Sin contexto previo relevante."
        prompt = f"""
Eres un resolutor interno para continuaciones de una practica matematica.

Hay una practica activa o reciente asociada a esta conversacion.
Decide si el mensaje actual continua ese ejercicio o si realmente abre otra tarea.

Mensaje actual:
{message}

Contexto reciente:
{history}

Estado pedagogico:
{json.dumps(agent_state, ensure_ascii=False)}

Si el mensaje retoma el mismo ejercicio activo o reciente, favorece:
- explain_practice_context
- grade_practice

Si claramente cambia de objetivo, usa una de:
- generate_practice
- answer_theory
- solve_exercise
- ask_clarification

No te bases en palabras exactas. Usa el hilo conversacional.

Devuelve solo JSON valido:
{{
  "actions":["explain_practice_context"],
  "reason":"continues recently completed exercise",
  "topic":"integral",
  "detail_level":"detailed"
}}
""".strip()
        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un planner interno. Devuelves solo JSON valido.",
                prompt=prompt,
                temperature=0.1,
            )
            payload = self._extract_json(raw)
        except (OllamaClientError, ValueError, json.JSONDecodeError):
            return None

        actions = self._normalize_actions(payload.get("actions"))
        if not actions:
            return None

        return ConversationPlan(
            actions=actions,
            reason=f"practice_follow_up_{payload.get('reason') or 'semantic_recovery'}",
            topic=str(payload.get("topic")) if payload.get("topic") is not None else None,
            detail_level=self._normalize_detail_level(payload.get("detail_level")),
        )

    def _plan_from_semantic_payload(self, payload: dict) -> ConversationPlan | None:
        intent = self._normalize_intent(payload.get("intent"))
        target = self._normalize_target(payload.get("target"))
        if intent not in self._allowed_intents or target not in self._allowed_targets:
            return None

        topic = payload.get("topic")
        if topic is not None:
            topic = str(topic)
        detail_level = self._normalize_detail_level(payload.get("detail_level"))
        confidence = self._normalize_confidence(payload.get("confidence"))
        reason = str(payload.get("reason") or intent)
        semantic_decision = SemanticPlannerDecision(
            intent=intent,
            target=target,
            reason=reason,
            confidence=confidence,
            topic=topic,
            detail_level=detail_level,
        )
        return self._semantic_decision_to_plan(semantic_decision)

    def _semantic_decision_to_plan(self, decision: SemanticPlannerDecision) -> ConversationPlan:
        if decision.intent == "mixed_theory_practice":
            return ConversationPlan(
                actions=["answer_theory", "generate_practice"],
                reason=f"semantic_{decision.reason}",
                topic=decision.topic,
                detail_level=decision.detail_level,
            )
        if decision.intent == "practice_request":
            return ConversationPlan(
                actions=["generate_practice"],
                reason=f"semantic_{decision.reason}",
                topic=decision.topic,
                detail_level=decision.detail_level,
            )
        if decision.intent == "explain_practice_context":
            return ConversationPlan(
                actions=["explain_practice_context"],
                reason=f"semantic_{decision.reason}",
                topic=decision.topic,
                detail_level="detailed",
            )
        if decision.intent == "grade_active_practice":
            return ConversationPlan(
                actions=["grade_practice"],
                reason=f"semantic_{decision.reason}",
                topic=decision.topic,
                detail_level=decision.detail_level,
            )
        if decision.intent == "solve_new_problem":
            return ConversationPlan(
                actions=["solve_exercise"],
                reason=f"semantic_{decision.reason}",
                topic=decision.topic,
                detail_level=decision.detail_level,
            )
        if decision.intent == "theory_request":
            return ConversationPlan(
                actions=["answer_theory"],
                reason=f"semantic_{decision.reason}",
                topic=decision.topic,
                detail_level=decision.detail_level,
            )
        return ConversationPlan(
            actions=["ask_clarification"],
            reason=f"semantic_{decision.reason}",
            topic=decision.topic,
            detail_level=decision.detail_level,
        )

    @staticmethod
    def _practice_context_summary(agent_state: dict, key: str) -> str:
        practice_context = dict(agent_state or {}).get(key) or {}
        if not practice_context:
            if key == "pending_practice":
                return "No hay practica activa."
            return "No hay practica reciente."
        return json.dumps(
            {
                "topic": practice_context.get("topic"),
                "problem_type": practice_context.get("problem_type"),
                "exercise_text": practice_context.get("exercise_text"),
                "expected_answer": practice_context.get("expected_answer"),
                "attempts": practice_context.get("attempts", 0),
                "last_outcome": practice_context.get("last_outcome"),
                "status": practice_context.get("status"),
            },
            ensure_ascii=False,
        )

    def _plan_with_rules(
        self,
        *,
        message: str,
        agent_state: dict,
    ) -> ConversationPlan:
        normalized = normalize_search_text(message)
        active_practice = agent_state.get("pending_practice")
        detected_topic = self._detect_topic(normalized)

        if active_practice and self._looks_like_practice_correction(
            normalized_message=normalized,
            pending_topic=str(active_practice.get("topic") or ""),
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

        if active_practice and self._looks_like_practice_attempt(
            normalized_message=normalized,
            pending_practice=active_practice,
        ):
            return ConversationPlan(
                actions=["grade_practice"],
                reason="rule_active_practice_answer",
                topic=str(active_practice.get("topic") or ""),
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
        active_practice = agent_state.get("pending_practice")
        detected_topic = self._detect_topic(normalized)
        detail_level = plan.detail_level

        if active_practice and self._looks_like_practice_correction(
            normalized_message=normalized,
            pending_topic=str(active_practice.get("topic") or ""),
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

        if active_practice and self._looks_like_practice_attempt(
            normalized_message=normalized,
            pending_practice=active_practice,
        ):
            return ConversationPlan(
                actions=["grade_practice"],
                reason="guardrail_active_practice",
                topic=str(active_practice.get("topic") or ""),
                detail_level=detail_level,
            )

        if active_practice and self._looks_like_theory_query(normalized):
            return ConversationPlan(
                actions=["answer_theory"],
                reason="guardrail_context_switch_theory",
                topic=detected_topic,
                detail_level=detail_level,
            )

        if active_practice and self._looks_like_new_math_task(
            message=message,
            normalized_message=normalized,
            pending_practice=active_practice,
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
    def _normalize_intent(cls, raw_value: object) -> PlannerIntent | None:
        legacy_map = {
            "grade_pending_practice": "grade_active_practice",
            "explain_pending_practice": "explain_practice_context",
        }
        normalized = legacy_map.get(str(raw_value), raw_value)
        if normalized in cls._allowed_intents:
            return normalized
        return None

    @classmethod
    def _normalize_target(cls, raw_value: object) -> PlannerTarget | None:
        legacy_map = {
            "pending_practice": "active_practice",
        }
        normalized = legacy_map.get(str(raw_value), raw_value)
        if normalized in cls._allowed_targets:
            return normalized
        return None

    @staticmethod
    def _normalize_confidence(raw_value: object) -> float:
        try:
            confidence = float(raw_value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, confidence))

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

    @classmethod
    def _looks_like_pending_practice_explanation_request(cls, normalized_message: str) -> bool:
        if not any(marker in normalized_message for marker in cls._pending_explanation_markers):
            return False
        return any(marker in normalized_message for marker in cls._pending_reference_markers) or any(
            marker in normalized_message for marker in ("paso a paso", "paso por paso", "procedimiento")
        )

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

    @staticmethod
    def _has_practice_context(agent_state: dict) -> bool:
        state = dict(agent_state or {})
        return bool(state.get("pending_practice") or state.get("last_practice_context"))

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
