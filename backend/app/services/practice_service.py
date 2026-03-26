from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sympy import Symbol, exp, series, simplify
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
from app.services.math_parser_service import MathParserService
from app.services.ollama_client import OllamaClient, OllamaClientError
from app.services.sympy_solver_service import SymPySolverService
from app.utils.expression_normalizer import normalize_text

if TYPE_CHECKING:
    from app.core.config import Settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PracticeGenerationResult:
    text: str
    state: dict


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


class PracticeService:
    _transformations = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )
    _continuation_patterns = (
        "otro",
        "otra",
        "uno mas",
        "uno más",
        "mas dificil",
        "más dificil",
        "mas retador",
        "más retador",
        "otra vez",
    )
    _topic_aliases = (
        ("serie_de_taylor", ("serie de taylor", "taylor")),
        ("newton_raphson", ("newton raphson", "newton-raphson")),
        ("regula_falsi", ("regula falsi", "falsa posicion", "falsa posición")),
        ("metodo_de_la_secante", ("metodo de la secante", "método de la secante", "secante")),
        ("punto_fijo", ("punto fijo",)),
        ("biseccion", ("biseccion", "bisección")),
        ("lagrange", ("lagrange",)),
        ("interpolacion_newton", ("interpolacion de newton", "interpolación de newton")),
        ("simpson_1_3", ("simpson 1/3", "simpson 1 3", "simpson un tercio")),
        ("trapecios", ("trapecio", "trapecios")),
        ("derivative", ("derivada", "derivadas", "derivar")),
        ("integral", ("integral", "integrales", "integrar")),
        ("limit", ("limite", "límite", "limites", "límites")),
        ("equation", ("ecuacion", "ecuación", "ecuaciones")),
    )

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
        template = self._select_template(request_text=request_text, current_state=current_state or {})

        if template.raw_input and not template.expected_answer:
            parsed = self.parser_service.parse(template.raw_input)
            solved = self.solver_service.solve(parsed)
            expected_answer = solved.final_result
            expected_sympy_input = solved.sympy_input
            problem_type = parsed.problem_type.value
        else:
            expected_answer = str(template.expected_answer or "").strip()
            expected_sympy_input = str(template.expected_sympy_input or expected_answer).strip()
            problem_type = template.problem_type

        pending_practice = {
            "kind": "practice",
            "topic": template.topic,
            "problem_type": problem_type,
            "raw_input": template.raw_input,
            "exercise_text": template.exercise_text,
            "expected_answer": expected_answer,
            "expected_sympy_input": expected_sympy_input,
            "hint": template.hint,
            "grading_mode": template.grading_mode,
            "rubric": template.rubric,
            "reference_summary": template.reference_summary,
            "keywords": template.keywords or [],
            "attempts": 0,
        }
        text = self._build_practice_prompt(
            exercise_text=template.exercise_text,
            hint=template.hint,
        )
        return PracticeGenerationResult(
            text=text,
            state={"pending_practice": pending_practice},
        )

    def grade_attempt(self, *, pending_practice: dict, student_message: str) -> PracticeGradeResult:
        student_answer = self._extract_student_answer(student_message)
        attempts = int(pending_practice.get("attempts", 0)) + 1
        grading_mode = str(pending_practice.get("grading_mode") or "symbolic")

        if grading_mode == "llm_rubric":
            return self._grade_with_llm_rubric(
                pending_practice=pending_practice,
                student_answer=student_answer,
                attempts=attempts,
            )

        if grading_mode == "keyword_rubric":
            return self._grade_with_keywords(
                pending_practice=pending_practice,
                student_answer=student_answer,
                attempts=attempts,
            )

        expected_answer = str(pending_practice.get("expected_answer", "")).strip()
        is_correct = self._answers_match(expected_answer=expected_answer, student_answer=student_answer)

        if is_correct:
            text = self._build_correct_feedback(
                exercise_text=str(pending_practice.get("exercise_text", "")),
                student_answer=student_answer,
                expected_answer=expected_answer,
            )
            return PracticeGradeResult(text=text, is_correct=True, next_state={})

        next_state = {
            "pending_practice": {
                **pending_practice,
                "attempts": attempts,
            }
        }
        text = self._build_incorrect_feedback(
            exercise_text=str(pending_practice.get("exercise_text", "")),
            student_answer=student_answer,
            expected_answer=expected_answer,
            hint=str(pending_practice.get("hint", "")),
            attempts=attempts,
        )
        return PracticeGradeResult(text=text, is_correct=False, next_state=next_state)

    def _select_template(self, *, request_text: str, current_state: dict) -> PracticeTemplate:
        resolved_topic, reference = self._resolve_requested_topic(
            request_text=request_text,
            current_state=current_state,
        )

        if resolved_topic == "integral":
            return PracticeTemplate(
                topic="integral",
                problem_type="integral",
                raw_input="Integral de 2*x + 3 dx",
                exercise_text="Resuelve esta integral: integral de 2*x + 3 dx.",
                hint="Piensa en la linealidad de la integral y en las potencias basicas.",
            )
        if resolved_topic == "limit":
            return PracticeTemplate(
                topic="limit",
                problem_type="limit",
                raw_input="lim x->0 sin(x)/x",
                exercise_text="Calcula este limite: lim x->0 sin(x)/x.",
                hint="Recuerda uno de los limites notables mas usados en calculo 1.",
            )
        if resolved_topic == "equation":
            return PracticeTemplate(
                topic="equation",
                problem_type="equation",
                raw_input="Resuelve 3*x - 5 = 16",
                exercise_text="Resuelve la ecuacion 3*x - 5 = 16.",
                hint="Despeja x paso a paso manteniendo el equilibrio en ambos lados.",
            )
        if resolved_topic == "serie_de_taylor":
            x = Symbol("x")
            expected = str(series(exp(x), x, 0, 4).removeO())
            return PracticeTemplate(
                topic="serie_de_taylor",
                problem_type="serie_de_taylor",
                exercise_text="Construye el polinomio de Taylor de orden 3 de e^x alrededor de x = 0.",
                hint="Calcula f(0), f'(0), f''(0) y f'''(0), y luego arma P3(x) con la formula general.",
                expected_answer=expected,
                expected_sympy_input=expected,
            )
        if resolved_topic == "derivative":
            return PracticeTemplate(
                topic="derivative",
                problem_type="derivative",
                raw_input="derivada de 3*x^2 + 2*x - 5",
                exercise_text="Deriva la funcion f(x) = 3*x^2 + 2*x - 5.",
                hint="Aplica la regla de la potencia termino a termino.",
            )

        return self._build_knowledge_grounded_template(
            topic=resolved_topic,
            request_text=request_text,
            reference=reference,
        )

    def _resolve_requested_topic(
        self,
        *,
        request_text: str,
        current_state: dict,
    ) -> tuple[str, KnowledgeSearchResult | None]:
        normalized = normalize_search_text(request_text)
        pending_practice = dict(current_state or {}).get("pending_practice") or {}

        for topic, aliases in self._topic_aliases:
            if any(alias in normalized for alias in aliases):
                return topic, self._find_reference(request_text)

        if any(pattern in normalized for pattern in self._continuation_patterns):
            pending_topic = str(pending_practice.get("topic") or "").strip()
            if pending_topic:
                return pending_topic, self._find_reference(pending_topic)

        reference = self._find_reference(request_text)
        if reference:
            return reference.document.topic, reference

        pending_topic = str(pending_practice.get("topic") or "").strip()
        if pending_topic:
            return pending_topic, self._find_reference(pending_topic)

        return "derivative", None

    def _find_reference(self, query: str) -> KnowledgeSearchResult | None:
        if not self.knowledge_base_service:
            return None
        matches = self.knowledge_base_service.search(query, limit=1)
        return matches[0] if matches else None

    def _build_knowledge_grounded_template(
        self,
        *,
        topic: str,
        request_text: str,
        reference: KnowledgeSearchResult | None,
    ) -> PracticeTemplate:
        if reference and self.ollama_client:
            try:
                return self._build_llm_grounded_template(
                    request_text=request_text,
                    reference=reference,
                )
            except OllamaClientError as exc:
                logger.warning("Falling back to conceptual practice template: %s", exc)
            except (ValueError, json.JSONDecodeError) as exc:
                logger.warning("Invalid practice JSON from Ollama, using fallback template: %s", exc)

        if reference:
            document = reference.document
            keywords = sorted(
                {
                    *document.tags,
                    *tokenize(document.topic),
                    *tokenize(document.subtopic),
                    *tokenize(document.text)[:6],
                }
            )
            title = document.title
            return PracticeTemplate(
                topic=document.topic,
                problem_type=document.topic,
                grading_mode="keyword_rubric",
                exercise_text=(
                    f"Vamos con una practica corta sobre {title}. "
                    f"Explica con tus palabras cual es la idea central de {title} "
                    "y menciona al menos una condicion, paso clave o criterio importante para aplicarlo bien."
                ),
                hint="Piensa en la intuicion principal del metodo y en que detalle tecnico evita cometer errores.",
                expected_answer=document.text,
                rubric=(
                    f"La respuesta debe reflejar la idea central de {title} "
                    "y mencionar al menos un criterio, paso o condicion de uso."
                ),
                reference_summary=document.text,
                keywords=keywords,
            )

        return PracticeTemplate(
            topic=topic,
            problem_type="derivative",
            raw_input="derivada de 3*x^2 + 2*x - 5",
            exercise_text="Deriva la funcion f(x) = 3*x^2 + 2*x - 5.",
            hint="Aplica la regla de la potencia termino a termino.",
        )

    def _build_llm_grounded_template(
        self,
        *,
        request_text: str,
        reference: KnowledgeSearchResult,
    ) -> PracticeTemplate:
        document = reference.document
        prompt = f"""
Tema pedido por el estudiante:
{request_text}

Tema recuperado del corpus:
- curso: {document.course}
- unidad: {document.unit}
- tema: {document.topic}
- subtema: {document.subtopic}
- texto base: {document.text}

Genera un solo ejercicio corto y util para practicar este tema.
REGLAS ESTRICTAS:
1. NO INVENTES NINGUN PROBLEMA MATEMATICO. Si el texto base menciona un ejemplo matematico, integrales o derivadas, DEBES usar EXACTAMENTE la misma expresion del texto base para crear el ejercicio.
2. Si inventas polinomios nuevos, el evaluador de simbologia fallara. Solo reutiliza la teoria de "texto base".
3. Si el tema es puramente teorico, pide una explicacion breve o justificada.
4. La respuesta esperada debe ser breve y clara.
5. Incluye una pista ('hint') corta.

Devuelve solo JSON valido con esta forma:
{{
  "exercise_text": "...",
  "expected_answer": "...",
  "hint": "...",
  "rubric": "...",
  "keywords": ["...", "..."]
}}
""".strip()
        raw = self.ollama_client.generate(
            system_prompt="Eres un generador interno de practica matematica. Devuelves solo JSON valido.",
            prompt=prompt,
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
            topic=document.topic,
            problem_type=document.topic,
            grading_mode="llm_rubric",
            exercise_text=exercise_text,
            expected_answer=expected_answer,
            hint=hint,
            rubric=rubric or f"La respuesta debe centrarse en {document.title}.",
            reference_summary=document.text,
            keywords=keywords or document.tags,
        )

    @staticmethod
    def _build_practice_prompt(*, exercise_text: str, hint: str) -> str:
        return (
            f"Claro. Te propongo este ejercicio:\n\n"
            f"{exercise_text}\n\n"
            "Intentalo tu primero. Si quieres, puedes escribirme solo tu resultado o contarme el procedimiento. "
            f"Si te atoras, te doy una pista: {hint}"
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
        if self.ollama_client:
            try:
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
""".strip()
                return self.ollama_client.generate(
                    system_prompt="Eres un tutor matematico cercano y preciso.",
                    prompt=prompt,
                ).strip()
            except OllamaClientError as exc:
                logger.warning("Falling back to template incorrect feedback: %s", exc)

        if attempts >= 2:
            return (
                f"No coincide todavia. La respuesta esperada es {expected_answer}. "
                "Si quieres, ahora te explico como llegar a ella paso a paso."
            )
        return (
            "Vas cerca, pero esa respuesta no coincide con lo esperado. "
            f"Revisa esta idea: {hint} "
            "Si quieres, intenta una vez mas y luego lo resolvemos juntos."
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

    def _answers_match(self, *, expected_answer: str, student_answer: str) -> bool:
        if not student_answer:
            return False

        expected = expected_answer.strip()
        student = student_answer.strip()
        
        # Unify 'C' and 'c' for integration constants so it doesn't fail symbolically
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
            difference = simplify(expected_expr - student_expr)
            return difference == 0
        except Exception:
            try:
                expected_eq = parse_expr(expected.replace("=", "-(") + ")", local_dict=self.local_dict.copy())
                student_eq = parse_expr(student.replace("=", "-(") + ")", local_dict=self.local_dict.copy())
                return simplify(expected_eq - student_eq) == 0
            except Exception:
                return False

    def _grade_with_llm_rubric(
        self,
        *,
        pending_practice: dict,
        student_answer: str,
        attempts: int,
    ) -> PracticeGradeResult:
        if self.ollama_client:
            try:
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
                raw = self.ollama_client.generate(
                    system_prompt="Eres un evaluador interno de practica matematica. Devuelves solo JSON valido.",
                    prompt=prompt,
                )
                payload = self._extract_json(raw)
                is_correct = bool(payload.get("is_correct"))
                feedback = str(payload.get("feedback", "")).strip()
                if feedback:
                    next_state = {} if is_correct else {
                        "pending_practice": {
                            **pending_practice,
                            "attempts": attempts,
                        }
                    }
                    return PracticeGradeResult(
                        text=feedback,
                        is_correct=is_correct,
                        next_state=next_state,
                    )
            except (OllamaClientError, ValueError, json.JSONDecodeError) as exc:
                logger.warning("Falling back to keyword practice grading: %s", exc)

        return self._grade_with_keywords(
            pending_practice=pending_practice,
            student_answer=student_answer,
            attempts=attempts,
        )

    def _grade_with_keywords(
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
        is_correct = len(overlap) >= min(2, len(keywords)) if keywords else False

        if is_correct:
            text = self._build_correct_feedback(
                exercise_text=str(pending_practice.get("exercise_text", "")),
                student_answer=student_answer,
                expected_answer=str(pending_practice.get("expected_answer", "")),
            )
            return PracticeGradeResult(text=text, is_correct=True, next_state={})

        next_state = {
            "pending_practice": {
                **pending_practice,
                "attempts": attempts,
            }
        }
        text = self._build_incorrect_feedback(
            exercise_text=str(pending_practice.get("exercise_text", "")),
            student_answer=student_answer,
            expected_answer=str(pending_practice.get("expected_answer", "")),
            hint=str(pending_practice.get("hint", "")),
            attempts=attempts,
        )
        return PracticeGradeResult(text=text, is_correct=False, next_state=next_state)

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
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error("JSON parse error: %s - Raw string: %s", e, json_str)
            raise ValueError(f"Invalid JSON generated: {e}")
