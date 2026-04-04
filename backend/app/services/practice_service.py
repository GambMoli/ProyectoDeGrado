from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sympy import Symbol, latex, series, simplify
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from app.services.knowledge_base_service import (
    KnowledgeBaseService,
    KnowledgeSearchResult,
    normalize_search_text,
    tokenize,
)
from app.services.math_parser_service import MathParserService, ParsedExercise
from app.services.ollama_client import OllamaClient, OllamaClientError
from app.services.sympy_solver_service import SymPySolverService
from app.utils.llm_text import normalize_llm_math_text
from app.utils.expression_normalizer import normalize_text

if TYPE_CHECKING:
    from app.core.config import Settings

logger = logging.getLogger(__name__)


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


class PracticeService:
    _transformations = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )
    _continuation_patterns = (
        "otro",
        "otra",
        "uno mas",
        "mas dificil",
        "mas retador",
        "otra vez",
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
        ("derivative", ("derivada", "derivadas", "derivar")),
        ("integral", ("integral", "integrales", "integrar")),
        ("limit", ("limite", "limites")),
        ("equation", ("ecuacion", "ecuaciones")),
    )
    _symbolic_topics = {"derivative", "integral", "limit", "equation"}
    _course_request_tokens = {
        "calculo",
        "1",
        "2",
        "metodos",
        "numericos",
        "ejercicio",
        "ejercicios",
        "practica",
        "practicar",
        "quiero",
        "dame",
        "ponme",
        "proponme",
        "curso",
        "tema",
        "temas",
    }
    _reference_symbolic_topics = {
        "antiderivadas_e_integrales_indefinidas": "integral",
        "integrales_definidas_y_sumas_de_riemann": "integral",
        "integracion_por_sustitucion_e_integracion_numerica": "integral",
        "integracion_por_partes": "integral",
        "metodo_de_sustitucion": "integral",
        "sustitucion_01": "integral",
        "por_partes_01": "integral",
        "fracciones_parciales": "integral",
        "integrales_impropias": "integral",
        "teorema_fundamental_del_calculo": "integral",
        "definicion_y_reglas_basicas_de_derivacion": "derivative",
        "limites_de_una_funcion": "limit",
        "continuidad_de_funciones": "limit",
        "serie_de_taylor": "serie_de_taylor",
    }
    _history_limit = 6

    def __init__(
        self,
        settings: Settings,
        parser_service: MathParserService,
        solver_service: SymPySolverService,
        ollama_client: OllamaClient | None = None,
        knowledge_base_service: KnowledgeBaseService | None = None,
    ) -> None:
        self.settings = settings
        self.parser_service = parser_service
        self.solver_service = solver_service
        self.ollama_client = ollama_client
        self.knowledge_base_service = knowledge_base_service
        self.local_dict = solver_service.local_dict.copy()

    def generate_practice(self, request_text: str, current_state: dict | None = None) -> PracticeGenerationResult:
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        state = current_state or {}
        template = self._select_template(request_text=request_text, current_state=state)
        history = self._build_updated_history(current_state=state, template=template)
        exercise_text = template.exercise_text

        if template.raw_input and not template.expected_answer:
            parsed = self.parser_service.parse(template.raw_input)
            solved = self.solver_service.solve(parsed)
            expected_answer = solved.final_result
            expected_sympy_input = solved.sympy_input
            problem_type = parsed.problem_type.value
            exercise_text = self._build_symbolic_exercise_text(parsed)
        else:
            expected_answer = str(template.expected_answer or "").strip()
            expected_sympy_input = str(template.expected_sympy_input or expected_answer).strip()
            problem_type = template.problem_type

        pending_practice = {
            "kind": "practice",
            "topic": template.topic,
            "problem_type": problem_type,
            "raw_input": template.raw_input,
            "exercise_text": exercise_text,
            "expected_answer": expected_answer,
            "expected_sympy_input": expected_sympy_input,
            "hint": template.hint,
            "grading_mode": template.grading_mode,
            "rubric": template.rubric,
            "reference_summary": template.reference_summary,
            "keywords": template.keywords or [],
            "attempts": 0,
            "practice_history": history,
        }
        text = self._build_practice_prompt(
            exercise_text=exercise_text,
            hint=template.hint,
        )
        return PracticeGenerationResult(
            text=text,
            state={
                "practice_history": history,
                "pending_practice": pending_practice,
            },
            exercise_text=exercise_text,
            hint=template.hint,
            topic=template.topic,
            problem_type=problem_type,
        )

    def grade_attempt(self, *, pending_practice: dict, student_message: str) -> PracticeGradeResult:
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        student_answer = self._extract_student_answer(student_message)
        attempts = int(pending_practice.get("attempts", 0)) + 1
        grading_mode = str(pending_practice.get("grading_mode") or "symbolic")

        if grading_mode == "llm_rubric":
            return self._grade_with_llm_rubric(
                pending_practice=pending_practice,
                student_answer=student_answer,
                attempts=attempts,
            )

        expected_answer = str(pending_practice.get("expected_answer", "")).strip()
        problem_type = str(pending_practice.get("problem_type") or "")
        is_correct = self._answers_match(
            expected_answer=expected_answer,
            student_answer=student_answer,
            problem_type=problem_type,
        )

        if is_correct:
            text = self._build_correct_feedback(
                exercise_text=str(pending_practice.get("exercise_text", "")),
                student_answer=student_answer,
                expected_answer=expected_answer,
            )
            return PracticeGradeResult(
                text=text,
                is_correct=True,
                next_state=self._build_state_from_pending(
                    pending_practice,
                    attempts=attempts,
                    last_outcome="correct",
                ),
            )

        next_state = self._build_state_from_pending(
            pending_practice,
            attempts=attempts,
            keep_pending=True,
        )
        text = self._build_incorrect_feedback(
            exercise_text=str(pending_practice.get("exercise_text", "")),
            student_answer=student_answer,
            expected_answer=expected_answer,
            hint=str(pending_practice.get("hint", "")),
            attempts=attempts,
        )
        return PracticeGradeResult(text=text, is_correct=False, next_state=next_state)

    def explain_practice_context(self, *, practice_context: dict, student_request: str) -> str:
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        prompt = f"""
Ejercicio de referencia:
{practice_context.get("exercise_text", "")}

Tema:
{practice_context.get("topic", "")}

Resultado correcto:
{practice_context.get("expected_answer", "")}

Pista base:
{practice_context.get("hint", "")}

Referencia conceptual:
{practice_context.get("reference_summary", "")}

Rubrica:
{practice_context.get("rubric", "")}

Peticion del estudiante:
{student_request}

Explica este mismo ejercicio de forma guiada.
- Desarrolla el procedimiento paso a paso.
- Para las expresiones matematicas usa LaTeX simple con delimitadores \\(...\\) o \\[...\\].
- Manten el foco en este ejercicio, no en teoria general suelta.
- No inventes un ejercicio distinto.
- Si el ejercicio es conceptual, explica la idea correcta y como responderlo mejor.
- No cierres con una pregunta obligatoria.
""".strip()
        try:
            text = self.ollama_client.generate(
                system_prompt="Eres un tutor matematico cercano y preciso.",
                prompt=prompt,
                temperature=0.2,
            )
            return normalize_llm_math_text(text)
        except OllamaClientError:
            return self._fallback_practice_context_explanation(
                exercise_text=str(practice_context.get("exercise_text", "")),
                expected_answer=str(practice_context.get("expected_answer", "")),
                hint=str(practice_context.get("hint", "")),
            )

    def _select_template(self, *, request_text: str, current_state: dict) -> PracticeTemplate:
        history = self._get_practice_history(current_state)
        strategy = self._infer_practice_strategy(
            request_text=request_text,
            current_state=current_state,
            history=history,
        )
        if strategy:
            return self._build_template_from_strategy(
                strategy=strategy,
                request_text=request_text,
                history=history,
            )

        resolved_topic, references = self._resolve_requested_topic(
            request_text=request_text,
            current_state=current_state,
        )
        return self._build_template_with_fallback_strategy(
            resolved_topic=resolved_topic,
            references=references,
            request_text=request_text,
            history=history,
        )

    def _build_template_from_strategy(
        self,
        *,
        strategy: PracticeStrategy,
        request_text: str,
        history: list[dict],
    ) -> PracticeTemplate:
        if strategy.generator_mode == "symbolic" and strategy.topic in self._symbolic_topics:
            return self._build_symbolic_template(
                topic=strategy.topic,
                request_text=request_text,
                references=strategy.references,
                history=history,
            )

        if strategy.generator_mode == "taylor" or strategy.topic == "serie_de_taylor":
            return self._build_taylor_template(
                request_text=request_text,
                references=strategy.references,
                history=history,
            )

        if strategy.references:
            return self._build_llm_grounded_template(
                request_text=request_text,
                references=strategy.references,
                history=history,
                requested_topic=strategy.topic,
            )

        return self._build_fallback_template(
            topic=strategy.topic if strategy.topic not in {"calculo_1", "calculo_2", "metodos_numericos"} else "derivative",
            history=history,
        )

    def _build_template_with_fallback_strategy(
        self,
        *,
        resolved_topic: str,
        references: list[KnowledgeSearchResult],
        request_text: str,
        history: list[dict],
    ) -> PracticeTemplate:

        if resolved_topic in self._symbolic_topics:
            return self._build_symbolic_template(
                topic=resolved_topic,
                request_text=request_text,
                references=references,
                history=history,
            )

        if resolved_topic == "serie_de_taylor":
            return self._build_taylor_template(
                request_text=request_text,
                references=references,
                history=history,
            )

        mapped_topic = self._map_reference_topic_to_generator(references)
        if mapped_topic in self._symbolic_topics:
            return self._build_symbolic_template(
                topic=mapped_topic,
                request_text=request_text,
                references=references,
                history=history,
                requested_topic=resolved_topic,
            )

        if mapped_topic == "serie_de_taylor":
            return self._build_taylor_template(
                request_text=request_text,
                references=references,
                history=history,
            )

        if references:
            return self._build_llm_grounded_template(
                request_text=request_text,
                references=references,
                history=history,
                requested_topic=resolved_topic,
            )

        fallback_topic = resolved_topic if resolved_topic not in {"calculo_1", "calculo_2", "metodos_numericos"} else "derivative"
        return self._build_fallback_template(
            topic=fallback_topic,
            history=history,
        )

    def _infer_practice_strategy(
        self,
        *,
        request_text: str,
        current_state: dict,
        history: list[dict],
    ) -> PracticeStrategy | None:
        if not self.ollama_client:
            return None

        state = dict(current_state or {})
        pending_practice = dict(state.get("pending_practice") or {})
        last_practice_context = dict(state.get("last_practice_context") or {})
        direct_references = self._find_references(request_text)
        course_hint = self.knowledge_base_service.detect_course_hint(request_text) if self.knowledge_base_service else None
        course_references = self._build_course_reference_pool(course_hint) if course_hint else []
        reference_pool = direct_references or course_references

        prompt = f"""
Eres un planner de practica matematica.
Tu trabajo es inferir semanticamente que tipo de ejercicio conviene proponer y sobre que tema.

Solicitud del estudiante:
{request_text}

Practica activa:
{json.dumps(self._compact_practice_context(pending_practice), ensure_ascii=False)}

Practica reciente:
{json.dumps(self._compact_practice_context(last_practice_context), ensure_ascii=False)}

Historial reciente de ejercicios:
{self._format_history_block(history)}

Referencias del corpus:
{self._format_reference_context(reference_pool)}

Elige:
- topic: derivative | integral | limit | equation | serie_de_taylor | biseccion | newton_raphson | regula_falsi | punto_fijo | lagrange | interpolacion_newton | trapecios | simpson_1_3 | calculo_1 | calculo_2 | metodos_numericos
- generator_mode: symbolic | taylor | conceptual

Reglas:
- Usa symbolic cuando convenga generar un ejercicio resoluble simbolicamente.
- Usa taylor solo para serie de Taylor.
- Usa conceptual cuando el tema no sea naturalmente simbolico o cuando la solicitud sea muy abierta y conceptual.
- Si el estudiante dice "otro" o continua, puedes retomar el tema activo o reciente.
- No te bases en palabras exactas; usa contexto y continuidad.

Devuelve solo JSON valido:
{{
  "topic":"integral",
  "generator_mode":"symbolic",
  "reason":"student wants a new integral exercise"
}}
""".strip()

        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un planner interno de practica matematica. Devuelves solo JSON valido.",
                prompt=prompt,
                temperature=0.2,
            )
            payload = self._extract_json(raw)
        except (OllamaClientError, ValueError, json.JSONDecodeError):
            return None

        topic = str(payload.get("topic") or "").strip()
        generator_mode = str(payload.get("generator_mode") or "").strip()
        if topic not in {
            "derivative",
            "integral",
            "limit",
            "equation",
            "serie_de_taylor",
            "biseccion",
            "newton_raphson",
            "regula_falsi",
            "punto_fijo",
            "lagrange",
            "interpolacion_newton",
            "trapecios",
            "simpson_1_3",
            "calculo_1",
            "calculo_2",
            "metodos_numericos",
        }:
            return None
        if generator_mode not in {"symbolic", "taylor", "conceptual"}:
            return None

        references = reference_pool or self._find_references(topic)
        if not references and topic in {"calculo_1", "calculo_2", "metodos_numericos"}:
            references = self._build_course_reference_pool(topic)

        return PracticeStrategy(
            topic=topic,
            generator_mode=generator_mode,
            references=references,
        )

    def _resolve_requested_topic(
        self,
        *,
        request_text: str,
        current_state: dict,
    ) -> tuple[str, list[KnowledgeSearchResult]]:
        normalized = normalize_search_text(request_text)
        pending_practice = dict(current_state or {}).get("pending_practice") or {}
        last_practice_context = dict(current_state or {}).get("last_practice_context") or {}
        course_hint = self.knowledge_base_service.detect_course_hint(request_text) if self.knowledge_base_service else None

        for topic, aliases in self._topic_aliases:
            if any(alias in normalized for alias in aliases):
                return topic, self._find_references(request_text)

        if any(pattern in normalized for pattern in self._continuation_patterns):
            pending_topic = str(pending_practice.get("topic") or "").strip()
            if pending_topic:
                return pending_topic, self._find_references(pending_topic)
            recent_topic = str(last_practice_context.get("topic") or "").strip()
            if recent_topic:
                return recent_topic, self._find_references(recent_topic)

        if course_hint and self._looks_like_course_request(normalized):
            return course_hint, self._build_course_reference_pool(course_hint)

        references = self._find_references(request_text)
        if references:
            return references[0].document.topic, references

        pending_topic = str(pending_practice.get("topic") or "").strip()
        if pending_topic:
            return pending_topic, self._find_references(pending_topic)

        recent_topic = str(last_practice_context.get("topic") or "").strip()
        if recent_topic:
            return recent_topic, self._find_references(recent_topic)

        return "derivative", []

    def _find_references(self, query: str, *, limit: int = 4) -> list[KnowledgeSearchResult]:
        if not self.knowledge_base_service:
            return []
        return self.knowledge_base_service.search(query, limit=limit)

    def _build_course_reference_pool(self, course: str, *, limit: int = 4) -> list[KnowledgeSearchResult]:
        if not self.knowledge_base_service:
            return []

        references: list[KnowledgeSearchResult] = []
        seen_topics: set[str] = set()
        for document in self.knowledge_base_service.get_course_documents(course):
            if document.topic in seen_topics:
                continue
            seen_topics.add(document.topic)
            references.append(
                KnowledgeSearchResult(
                    document=document,
                    score=1.0,
                    matched_terms=[course],
                )
            )
            if len(references) >= limit:
                break
        return references

    def _looks_like_course_request(self, normalized_request: str) -> bool:
        query_tokens = set(tokenize(normalized_request))
        if not query_tokens:
            return False
        return query_tokens.issubset(self._course_request_tokens)

    def _map_reference_topic_to_generator(self, references: list[KnowledgeSearchResult]) -> str | None:
        for reference in references:
            mapped = self._reference_symbolic_topics.get(reference.document.topic)
            if mapped:
                return mapped
        return None

    def _build_symbolic_template(
        self,
        *,
        topic: str,
        request_text: str,
        references: list[KnowledgeSearchResult],
        history: list[dict],
        requested_topic: str | None = None,
    ) -> PracticeTemplate:
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        topic_label = {
            "derivative": "derivadas",
            "integral": "integrales",
            "limit": "limites",
            "equation": "ecuaciones",
        }[topic]
        reference_context = self._format_reference_context(references)
        history_block = self._format_history_block(history)
        requested_topic_line = f"Tema del corpus a respetar: {requested_topic}\n" if requested_topic else ""
        prompt = f"""
Solicitud del estudiante:
{request_text}

Objetivo matematico:
{topic_label}
{requested_topic_line}Contexto del corpus:
{reference_context}

Ejercicios recientes para NO repetir:
{history_block}

Genera un ejercicio nuevo y breve.
- Usa el corpus como guia conceptual, no como texto a copiar.
- Puedes crear una expresion nueva si sigue fiel al tema.
- Debe ser resoluble por un evaluador simbolico.
- Usa solo la variable x.
- Mantente en dificultad basica o media.
- No repitas expresiones recientes ni hagas cambios triviales de coeficientes.

Formatos permitidos para raw_input:
- derivative: "derivada de <expresion>"
- integral: "integral de <expresion> dx"
- equation: "Resuelve <lado_izq> = <lado_der>"
- limit: "lim x->a <expresion>"

Devuelve solo JSON valido:
{{
  "mode": "symbolic",
  "raw_input": "...",
  "exercise_text": "...",
  "hint": "..."
}}
""".strip()
        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un generador interno de practica matematica. Devuelves solo JSON valido.",
                prompt=prompt,
                temperature=0.7,
            )
            payload = self._extract_json(raw)
            raw_input = str(payload.get("raw_input", "")).strip()
            exercise_text = str(payload.get("exercise_text", "")).strip()
            hint = str(payload.get("hint", "")).strip()
            if not raw_input or not hint:
                raise ValueError("Missing symbolic practice fields.")
            parsed = self.parser_service.parse(raw_input)
            solved = self.solver_service.solve(parsed)
            exercise_text = self._build_symbolic_exercise_text(parsed)
            return PracticeTemplate(
                topic=requested_topic or topic,
                problem_type=parsed.problem_type.value,
                raw_input=raw_input,
                exercise_text=exercise_text,
                hint=hint,
                expected_answer=solved.final_result,
                expected_sympy_input=solved.sympy_input,
                grading_mode="symbolic",
                reference_summary=self._reference_summary(references),
                keywords=self._keywords_from_references(references),
            )
        except Exception as exc:
            logger.warning("Falling back to deterministic symbolic practice for %s: %s", topic, exc)
            return self._build_fallback_template(
                topic=topic,
                history=history,
                reference_summary=self._reference_summary(references),
                keywords=self._keywords_from_references(references),
                topic_label=requested_topic or topic,
            )

    def _build_taylor_template(
        self,
        *,
        request_text: str,
        references: list[KnowledgeSearchResult],
        history: list[dict],
    ) -> PracticeTemplate:
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        reference_context = self._format_reference_context(references)
        history_block = self._format_history_block(history)
        prompt = f"""
Solicitud del estudiante:
{request_text}

Tema objetivo:
Serie de Taylor

Contexto del corpus:
{reference_context}

Ejercicios recientes para NO repetir:
{history_block}

Genera un ejercicio nuevo de polinomio de Taylor.
- Usa el corpus como base conceptual, no como copia.
- Escoge una funcion segura para manipular simbolicamente.
- Usa solo x como variable.
- Trabaja alrededor de x = 0.
- Usa orden 2, 3 o 4.
- Evita repetir la misma funcion del historial.

Funciones permitidas:
- exp(x)
- sin(x)
- cos(x)
- log(1 + x)
- 1/(1 - x)

Devuelve solo JSON valido:
{{
  "mode": "taylor",
  "function_expr": "...",
  "center": "0",
  "order": 3,
  "exercise_text": "...",
  "hint": "..."
}}
""".strip()
        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un generador interno de practica matematica. Devuelves solo JSON valido.",
                prompt=prompt,
                temperature=0.65,
            )
            payload = self._extract_json(raw)
            function_expr = str(payload.get("function_expr", "")).strip()
            center = str(payload.get("center", "0")).strip() or "0"
            order = int(payload.get("order", 3))
            exercise_text = str(payload.get("exercise_text", "")).strip()
            hint = str(payload.get("hint", "")).strip()
            if not function_expr or not hint:
                raise ValueError("Missing Taylor practice fields.")
            x = Symbol("x")
            expr = parse_expr(
                function_expr,
                local_dict=self.local_dict.copy(),
                transformations=self._transformations,
                evaluate=True,
            )
            center_expr = parse_expr(
                center,
                local_dict=self.local_dict.copy(),
                transformations=self._transformations,
                evaluate=True,
            )
            expected = str(series(expr, x, center_expr, order + 1).removeO())
            if not exercise_text:
                exercise_text = (
                    f"Construye el polinomio de Taylor de orden {order} de {function_expr} "
                    f"alrededor de x = {center}."
                )
            return PracticeTemplate(
                topic="serie_de_taylor",
                problem_type="serie_de_taylor",
                exercise_text=exercise_text,
                hint=hint,
                expected_answer=expected,
                expected_sympy_input=expected,
                grading_mode="symbolic",
                reference_summary=self._reference_summary(references),
                keywords=self._keywords_from_references(references),
            )
        except Exception as exc:
            logger.warning("Falling back to deterministic Taylor practice: %s", exc)
            return self._build_fallback_template(
                topic="serie_de_taylor",
                history=history,
                reference_summary=self._reference_summary(references),
                keywords=self._keywords_from_references(references),
            )

    def _build_llm_grounded_template(
        self,
        *,
        request_text: str,
        references: list[KnowledgeSearchResult],
        history: list[dict],
        requested_topic: str | None = None,
    ) -> PracticeTemplate:
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        prompt = f"""
Solicitud del estudiante:
{request_text}

Tema solicitado o inferido:
{requested_topic or references[0].document.topic}

Contexto del corpus:
{self._format_reference_context(references)}

Ejercicios recientes para NO repetir:
{self._format_history_block(history)}

Genera un solo ejercicio breve y util.
- Usa el corpus como base, pero redacta y construye una variante nueva.
- No copies frases completas ni reutilices exactamente el mismo ejemplo.
- Si el tema se presta a una pregunta conceptual, pide una explicacion corta o una justificacion concreta.
- La respuesta esperada debe ser breve y fiel al tema.
- Incluye una pista corta.

Devuelve solo JSON valido con esta forma:
{{
  "exercise_text": "...",
  "expected_answer": "...",
  "hint": "...",
  "rubric": "...",
  "keywords": ["...", "..."]
}}
""".strip()
        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un generador interno de practica matematica. Devuelves solo JSON valido.",
                prompt=prompt,
                temperature=0.65,
            )
            payload = self._extract_json(raw)
            exercise_text = str(payload.get("exercise_text", "")).strip()
            expected_answer = str(payload.get("expected_answer", "")).strip()
            hint = str(payload.get("hint", "")).strip()
            rubric = str(payload.get("rubric", "")).strip()
            raw_keywords = payload.get("keywords") or []
            keywords = [str(item).strip() for item in raw_keywords if str(item).strip()]
            if not exercise_text or not expected_answer or not hint:
                raise ValueError("Missing fields in LLM practice template.")
            return PracticeTemplate(
                topic=requested_topic or references[0].document.topic,
                problem_type=requested_topic or references[0].document.topic,
                grading_mode="llm_rubric",
                exercise_text=exercise_text,
                expected_answer=expected_answer,
                hint=hint,
                rubric=rubric or f"La respuesta debe centrarse en {references[0].document.title}.",
                reference_summary=self._reference_summary(references),
                keywords=keywords or self._keywords_from_references(references),
            )
        except Exception as exc:
            logger.warning("Falling back to conceptual practice for %s: %s", requested_topic, exc)
            reference = references[0]
            return PracticeTemplate(
                topic=requested_topic or reference.document.topic,
                problem_type=requested_topic or reference.document.topic,
                grading_mode="llm_rubric",
                exercise_text=(
                    f"Explica con tus palabras la idea principal de {reference.document.title} "
                    "y menciona un caso en el que se use."
                ),
                expected_answer=reference.document.text,
                hint="Piensa en la definicion central y en para que sirve el metodo o concepto.",
                rubric=f"La respuesta debe recoger la idea principal de {reference.document.title} y un uso razonable.",
                reference_summary=self._reference_summary(references),
                keywords=self._keywords_from_references(references),
            )

    def _build_fallback_template(
        self,
        *,
        topic: str,
        history: list[dict],
        reference_summary: str | None = None,
        keywords: list[str] | None = None,
        topic_label: str | None = None,
    ) -> PracticeTemplate:
        signature_count = self._history_topic_count(history, topic_label or topic)
        if topic == "integral":
            options = (
                PracticeTemplate(
                    topic=topic_label or "integral",
                    problem_type="integral",
                    raw_input="integral de x^2 + 4*x + 1 dx",
                    exercise_text="Resuelve esta integral: integral de x^2 + 4*x + 1 dx.",
                    hint="Integra termino a termino usando la regla de la potencia.",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
                PracticeTemplate(
                    topic=topic_label or "integral",
                    problem_type="integral",
                    raw_input="integral de sin(x) + 3*x dx",
                    exercise_text="Resuelve esta integral: integral de sin(x) + 3*x dx.",
                    hint="Separa la integral en dos partes y usa linealidad.",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
                PracticeTemplate(
                    topic=topic_label or "integral",
                    problem_type="integral",
                    raw_input="integral de (2*x + 1)^2 dx",
                    exercise_text="Resuelve esta integral: integral de (2*x + 1)^2 dx.",
                    hint="Puedes expandir primero el cuadrado antes de integrar.",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
            )
            return options[signature_count % len(options)]

        if topic == "limit":
            options = (
                PracticeTemplate(
                    topic=topic_label or "limit",
                    problem_type="limit",
                    raw_input="lim x->0 (exp(x) - 1)/x",
                    exercise_text="Calcula este limite: lim x->0 (exp(x) - 1)/x.",
                    hint="Recuerda el comportamiento de e^x cerca de 0.",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
                PracticeTemplate(
                    topic=topic_label or "limit",
                    problem_type="limit",
                    raw_input="lim x->0 (1 - cos(x))/x^2",
                    exercise_text="Calcula este limite: lim x->0 (1 - cos(x))/x^2.",
                    hint="Piensa en un limite notable trigonometrico o en una expansion local.",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
                PracticeTemplate(
                    topic=topic_label or "limit",
                    problem_type="limit",
                    raw_input="lim x->0 sin(3*x)/x",
                    exercise_text="Calcula este limite: lim x->0 sin(3*x)/x.",
                    hint="Reescribe la expresion para usar sin(u)/u.",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
            )
            return options[signature_count % len(options)]

        if topic == "equation":
            options = (
                PracticeTemplate(
                    topic=topic_label or "equation",
                    problem_type="equation",
                    raw_input="Resuelve 4*x - 7 = 13",
                    exercise_text="Resuelve la ecuacion 4*x - 7 = 13.",
                    hint="Despeja x manteniendo el equilibrio en ambos lados.",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
                PracticeTemplate(
                    topic=topic_label or "equation",
                    problem_type="equation",
                    raw_input="Resuelve 5*x + 9 = 2*x + 21",
                    exercise_text="Resuelve la ecuacion 5*x + 9 = 2*x + 21.",
                    hint="Reune las x en un lado y los numeros en el otro.",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
                PracticeTemplate(
                    topic=topic_label or "equation",
                    problem_type="equation",
                    raw_input="Resuelve 7*(x - 1) = 21",
                    exercise_text="Resuelve la ecuacion 7*(x - 1) = 21.",
                    hint="Empieza simplificando o dividiendo ambos lados entre 7.",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
            )
            return options[signature_count % len(options)]

        if topic == "serie_de_taylor":
            options = (
                PracticeTemplate(
                    topic="serie_de_taylor",
                    problem_type="serie_de_taylor",
                    exercise_text="Construye el polinomio de Taylor de orden 3 de e^x alrededor de x = 0.",
                    hint="Calcula derivadas sucesivas en 0 y arma el polinomio sin el termino O.",
                    expected_answer="x**3/6 + x**2/2 + x + 1",
                    expected_sympy_input="x**3/6 + x**2/2 + x + 1",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
                PracticeTemplate(
                    topic="serie_de_taylor",
                    problem_type="serie_de_taylor",
                    exercise_text="Construye el polinomio de Taylor de orden 4 de sin(x) alrededor de x = 0.",
                    hint="Alterna derivadas de sin y cos, y conserva solo hasta grado 4.",
                    expected_answer="-x**3/6 + x",
                    expected_sympy_input="-x**3/6 + x",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
                PracticeTemplate(
                    topic="serie_de_taylor",
                    problem_type="serie_de_taylor",
                    exercise_text="Construye el polinomio de Taylor de orden 4 de cos(x) alrededor de x = 0.",
                    hint="Recuerda que cos(x) aporta solo potencias pares cerca de 0.",
                    expected_answer="x**4/24 - x**2/2 + 1",
                    expected_sympy_input="x**4/24 - x**2/2 + 1",
                    reference_summary=reference_summary,
                    keywords=keywords,
                ),
            )
            return options[signature_count % len(options)]

        options = (
            PracticeTemplate(
                topic=topic_label or "derivative",
                problem_type="derivative",
                raw_input="derivada de 4*x^3 - x + 6",
                exercise_text="Deriva la funcion f(x) = 4*x^3 - x + 6.",
                hint="Aplica la regla de la potencia termino a termino.",
                reference_summary=reference_summary,
                keywords=keywords,
            ),
            PracticeTemplate(
                topic=topic_label or "derivative",
                problem_type="derivative",
                raw_input="derivada de sin(x) + x^2",
                exercise_text="Deriva la funcion f(x) = sin(x) + x^2.",
                hint="Combina la derivada trigonometrica con la regla de la potencia.",
                reference_summary=reference_summary,
                keywords=keywords,
            ),
            PracticeTemplate(
                topic=topic_label or "derivative",
                problem_type="derivative",
                raw_input="derivada de x^4 - 3*x^2 + 2*x",
                exercise_text="Deriva la funcion f(x) = x^4 - 3*x^2 + 2*x.",
                hint="Deriva cada termino por separado y luego simplifica.",
                reference_summary=reference_summary,
                keywords=keywords,
            ),
        )
        return options[signature_count % len(options)]

    @staticmethod
    def _build_practice_prompt(*, exercise_text: str, hint: str) -> str:
        return (
            "Vamos con un ejercicio para practicar.\n\n"
            f"Ejercicio:\n{exercise_text}\n\n"
            "Intentalo por tu cuenta primero. Puedes escribirme solo el resultado o contarme el procedimiento.\n\n"
            f"Pista:\n{hint}"
        )

    def _build_correct_feedback(
        self,
        *,
        exercise_text: str,
        student_answer: str,
        expected_answer: str,
    ) -> str:
        return (
            f"Si, ese resultado esta correcto: {expected_answer}. "
            "Coincide con la respuesta esperada y la idea del ejercicio esta bien aplicada. "
            "Si quieres, ahora revisamos el procedimiento paso a paso o te propongo uno un poco mas retador."
        )

    def _build_incorrect_feedback(
        self,
        *,
        exercise_text: str,
        student_answer: str,
        expected_answer: str,
        hint: str,
        attempts: int,
    ) -> str:
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        prompt = f"""
Ejercicio propuesto:
{exercise_text}

Respuesta del estudiante:
{student_answer}

Resultado correcto verificado:
{expected_answer}

Pista base:
{hint}

Intento actual:
{attempts}

Redacta una devolucion breve, natural y pedagogica.
- No digas que todo esta bien si no coincide.
- Senala con tacto que hay un error.
- Da una pista util sin resolver por completo en el primer intento.
- Si ya van varios intentos, puedes ser un poco mas explicito.
- No uses markdown decorativo.
- Si escribes una expresion matematica, usa LaTeX simple con delimitadores \\(...\\).
""".strip()
        try:
            text = self.ollama_client.generate(
                system_prompt="Eres un tutor matematico cercano y preciso.",
                prompt=prompt,
                temperature=0.35,
            ).strip()
            return normalize_llm_math_text(text)
        except OllamaClientError:
            return self._fallback_incorrect_feedback(
                student_answer=student_answer,
                expected_answer=expected_answer,
                hint=hint,
                attempts=attempts,
            )

    @staticmethod
    def _extract_student_answer(message: str) -> str:
        normalized = normalize_text(message)
        lowered = normalized.lower()
        answer = re.sub(
            r"(?i)^(el resultado es|mi resultado es|mi respuesta es|resultado:|respuesta:|creo que es|es)\s*",
            "",
            normalized,
        ).strip()
        if "=" in answer and any(token in lowered for token in ["resultado", "respuesta", "derivada", "integral"]):
            answer = answer.split("=", maxsplit=1)[1].strip()
        return answer

    def _answers_match(
        self,
        *,
        expected_answer: str,
        student_answer: str,
        problem_type: str = "",
    ) -> bool:
        if not student_answer:
            return False

        expected = expected_answer.strip()
        student = student_answer.strip()

        expected = expected.replace("+ C", "+ c").replace("+C", "+c")
        student = student.replace("+ C", "+ c").replace("+C", "+c")

        if expected == student:
            return True

        if expected.startswith("x = "):
            expected = expected.split("=", maxsplit=1)[1].strip()
        if student.startswith("x = "):
            student = student.split("=", maxsplit=1)[1].strip()

        try:
            expected_expr = parse_expr(
                expected,
                local_dict=self.local_dict.copy(),
                transformations=self._transformations,
                evaluate=True,
            )
            student_expr = parse_expr(
                student,
                local_dict=self.local_dict.copy(),
                transformations=self._transformations,
                evaluate=True,
            )
            if problem_type == "integral" and self._integral_answers_match(
                expected_expr=expected_expr,
                student_expr=student_expr,
            ):
                return True
            difference = simplify(expected_expr - student_expr)
            return difference == 0
        except Exception:
            try:
                expected_eq = parse_expr(expected.replace("=", "-(") + ")", local_dict=self.local_dict.copy())
                student_eq = parse_expr(student.replace("=", "-(") + ")", local_dict=self.local_dict.copy())
                return simplify(expected_eq - student_eq) == 0
            except Exception:
                return False

    @staticmethod
    def _integral_answers_match(*, expected_expr, student_expr) -> bool:
        free_symbols = sorted(
            {
                symbol
                for symbol in expected_expr.free_symbols.union(student_expr.free_symbols)
                if symbol.name != "c"
            },
            key=lambda item: item.name,
        )
        variable = free_symbols[0] if free_symbols else Symbol("x")
        return simplify((expected_expr - student_expr).diff(variable)) == 0

    @staticmethod
    def _fallback_incorrect_feedback(
        *,
        student_answer: str,
        expected_answer: str,
        hint: str,
        attempts: int,
    ) -> str:
        if attempts <= 1:
            return (
                "No coincide todavia con la respuesta esperada. "
                f"Revisa tu expresion y usa esta pista: {hint}"
            )
        return (
            "Aun hay un detalle por corregir. "
            f"La referencia esperada es {expected_answer}. "
            "Comparala con tu resultado y ajusta el paso donde te desviaste."
        )

    @staticmethod
    def _fallback_practice_context_explanation(
        *,
        exercise_text: str,
        expected_answer: str,
        hint: str,
    ) -> str:
        return (
            f"Vamos a desarrollar este ejercicio: {exercise_text} "
            f"La referencia correcta es {expected_answer}. "
            f"La idea clave para resolverlo es: {hint}"
        ).strip()

    def _fallback_llm_rubric_grade(
        self,
        *,
        pending_practice: dict,
        student_answer: str,
        attempts: int,
    ) -> PracticeGradeResult:
        keywords = [
            str(keyword).strip().lower()
            for keyword in pending_practice.get("keywords", [])
            if str(keyword).strip()
        ]
        student_tokens = set(tokenize(student_answer))
        overlap = {keyword for keyword in keywords if keyword in student_tokens}
        min_hits = min(2, len(keywords)) if keywords else 0
        is_correct = bool(keywords) and len(overlap) >= min_hits

        if is_correct:
            feedback = (
                "Tu respuesta recoge la idea principal del tema, asi que la doy por correcta. "
                "Si quieres, la afinamos o pasamos a una variante mas retadora."
            )
        else:
            feedback = (
                "No pude usar el evaluador automatico en este momento. "
                "Tu respuesta todavia no muestra con suficiente claridad la idea central del tema. "
                f"Apoyate en esta pista: {pending_practice.get('hint', '')}"
            ).strip()

        next_state = self._build_state_from_pending(
            pending_practice,
            attempts=attempts,
            keep_pending=not is_correct,
            last_outcome="correct" if is_correct else "incorrect",
        )
        return PracticeGradeResult(
            text=feedback,
            is_correct=is_correct,
            next_state=next_state,
        )

    def _grade_with_llm_rubric(
        self,
        *,
        pending_practice: dict,
        student_answer: str,
        attempts: int,
    ) -> PracticeGradeResult:
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        prompt = f"""
Ejercicio:
{pending_practice.get("exercise_text", "")}

Respuesta esperada:
{pending_practice.get("expected_answer", "")}

Rubrica:
{pending_practice.get("rubric", "")}

Pista base:
{pending_practice.get("hint", "")}

Respuesta del estudiante:
{student_answer}

Evalua si la respuesta es suficientemente correcta para este nivel.
- Considera correcta una respuesta breve si recoge la idea esencial del tema.
- Si es incorrecta o incompleta, senala con tacto que falta.
- No inventes contenido fuera del tema.

Devuelve solo JSON valido:
{{"is_correct": true, "feedback": "..."}}
""".strip()
        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un evaluador interno de practica matematica. Devuelves solo JSON valido.",
                prompt=prompt,
                temperature=0.25,
            )
            payload = self._extract_json(raw)
            is_correct = bool(payload.get("is_correct"))
            feedback = str(payload.get("feedback", "")).strip()
            if feedback:
                next_state = self._build_state_from_pending(
                    pending_practice,
                    attempts=attempts,
                    keep_pending=not is_correct,
                    last_outcome="correct" if is_correct else "incorrect",
                )
                return PracticeGradeResult(
                    text=feedback,
                    is_correct=is_correct,
                    next_state=next_state,
                )
        except (OllamaClientError, ValueError, json.JSONDecodeError):
            pass

        return self._fallback_llm_rubric_grade(
            pending_practice=pending_practice,
            student_answer=student_answer,
            attempts=attempts,
        )

    def _build_state_from_pending(
        self,
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
            next_state["last_practice_context"] = self._snapshot_practice_context(
                pending_practice,
                attempts=attempts,
                last_outcome=last_outcome or "completed",
            )
        return next_state

    @staticmethod
    def _snapshot_practice_context(
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

    def _get_practice_history(self, current_state: dict) -> list[dict]:
        history = list((current_state or {}).get("practice_history") or [])
        cleaned_history: list[dict] = []
        for entry in history[-self._history_limit :]:
            if isinstance(entry, dict):
                cleaned_history.append(
                    {
                        "topic": str(entry.get("topic", "")).strip(),
                        "signature": str(entry.get("signature", "")).strip(),
                        "exercise_text": str(entry.get("exercise_text", "")).strip(),
                    }
                )
        return cleaned_history

    def _build_updated_history(self, *, current_state: dict, template: PracticeTemplate) -> list[dict]:
        history = self._get_practice_history(current_state)
        signature_source = template.raw_input or template.expected_sympy_input or template.exercise_text
        history.append(
            {
                "topic": template.topic,
                "signature": signature_source.strip(),
                "exercise_text": template.exercise_text.strip(),
            }
        )
        return history[-self._history_limit :]

    @staticmethod
    def _format_reference_context(references: list[KnowledgeSearchResult]) -> str:
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

    @staticmethod
    def _format_history_block(history: list[dict]) -> str:
        if not history:
            return "No hay historial previo."
        lines = []
        for entry in history[-4:]:
            topic = entry.get("topic", "")
            signature = entry.get("signature", "")
            lines.append(f"- {topic}: {signature}")
        return "\n".join(lines)

    @staticmethod
    def _compact_practice_context(practice_context: dict) -> dict:
        if not practice_context:
            return {}
        return {
            "topic": practice_context.get("topic"),
            "problem_type": practice_context.get("problem_type"),
            "exercise_text": practice_context.get("exercise_text"),
            "last_outcome": practice_context.get("last_outcome"),
            "status": practice_context.get("status"),
        }

    def _build_symbolic_exercise_text(self, parsed: ParsedExercise) -> str:
        instruction = {
            "integral": "Calcula la integral indefinida de la funcion:",
            "derivative": "Calcula la derivada de la funcion:",
            "limit": "Calcula el limite:",
            "equation": "Resuelve la ecuacion:",
            "simplification": "Simplifica la expresion:",
        }.get(parsed.problem_type.value, "Trabaja este ejercicio:")
        formula = self._build_display_formula(parsed)
        return f"{instruction}\n\\[\n{formula}\n\\]"

    def _build_display_formula(self, parsed: ParsedExercise) -> str:
        if parsed.problem_type.value == "integral":
            variable = parsed.variable or "x"
            expression = self._expression_to_latex(parsed.expression)
            return f"\\int {expression}\\, d{variable}"

        if parsed.problem_type.value == "derivative":
            variable = parsed.variable or "x"
            expression = self._expression_to_latex(parsed.expression)
            return f"\\frac{{d}}{{d{variable}}}\\left({expression}\\right)"

        if parsed.problem_type.value == "limit":
            variable = parsed.variable or "x"
            point = parsed.limit_point or "0"
            expression = self._expression_to_latex(parsed.expression)
            return f"\\lim_{{{variable} \\to {point}}} {expression}"

        if parsed.problem_type.value == "equation" and "=" in parsed.expression:
            left, right = parsed.expression.split("=", maxsplit=1)
            return f"{self._expression_to_latex(left)} = {self._expression_to_latex(right)}"

        return self._expression_to_latex(parsed.expression)

    def _expression_to_latex(self, expression: str) -> str:
        normalized = normalize_text(expression).strip()
        try:
            parsed_expression = parse_expr(
                normalized,
                local_dict=self.local_dict.copy(),
                transformations=self._transformations,
                evaluate=False,
            )
            return latex(parsed_expression)
        except Exception:
            fallback = normalized.replace("**", "^").replace("*", " ")
            fallback = re.sub(r"exp\(([^()]+)\)", r"e^{\1}", fallback)
            return fallback

    @staticmethod
    def _reference_summary(references: list[KnowledgeSearchResult]) -> str | None:
        if not references:
            return None
        return " ".join(reference.document.text for reference in references[:2]).strip()

    @staticmethod
    def _keywords_from_references(references: list[KnowledgeSearchResult]) -> list[str]:
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

    @staticmethod
    def _history_topic_count(history: list[dict], topic: str) -> int:
        return sum(1 for entry in history if str(entry.get("topic", "")).strip() == topic)

    @staticmethod
    def _extract_json(raw: str) -> dict:
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.endswith("```"):
            raw = raw[:-3]

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object found in practice response. Raw: {raw}")
        json_str = match.group(0)

        json_str = re.sub(r'\\(?=[^"\\/bfnrtu])', r'\\\\', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as exc:
            logger.error("JSON parse error: %s - Raw string: %s", exc, json_str)
            raise ValueError(f"Invalid JSON generated: {exc}") from exc
