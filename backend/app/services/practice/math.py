from __future__ import annotations

import json
import logging
import re
from typing import Any

from sympy import Symbol, latex, simplify
from sympy.parsing.sympy_parser import parse_expr

from app.services.math_parser_service import ParsedExercise
from app.utils.expression_normalizer import normalize_text

logger = logging.getLogger(__name__)


def extract_student_answer(message: str) -> str:
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


def answers_match(
    *,
    expected_answer: str,
    student_answer: str,
    problem_type: str,
    local_dict: dict[str, Any],
    transformations: tuple[Any, ...],
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
            local_dict=local_dict.copy(),
            transformations=transformations,
            evaluate=True,
        )
        student_expr = parse_expr(
            student,
            local_dict=local_dict.copy(),
            transformations=transformations,
            evaluate=True,
        )
        if problem_type == "integral" and integral_answers_match(
            expected_expr=expected_expr,
            student_expr=student_expr,
        ):
            return True
        difference = simplify(expected_expr - student_expr)
        return difference == 0
    except Exception:
        try:
            expected_eq = parse_expr(
                expected.replace("=", "-(") + ")",
                local_dict=local_dict.copy(),
            )
            student_eq = parse_expr(
                student.replace("=", "-(") + ")",
                local_dict=local_dict.copy(),
            )
            return simplify(expected_eq - student_eq) == 0
        except Exception:
            return False


def integral_answers_match(*, expected_expr: Any, student_expr: Any) -> bool:
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


def build_symbolic_exercise_text(
    parsed: ParsedExercise,
    *,
    local_dict: dict[str, Any],
    transformations: tuple[Any, ...],
) -> str:
    instruction = {
        "integral": "Calcula la integral indefinida de la funcion:",
        "derivative": "Calcula la derivada de la funcion:",
        "limit": "Calcula el limite:",
        "equation": "Resuelve la ecuacion:",
        "simplification": "Simplifica la expresion:",
    }.get(parsed.problem_type.value, "Trabaja este ejercicio:")
    formula = build_display_formula(
        parsed,
        local_dict=local_dict,
        transformations=transformations,
    )
    return f"{instruction}\n\\[\n{formula}\n\\]"


def build_display_formula(
    parsed: ParsedExercise,
    *,
    local_dict: dict[str, Any],
    transformations: tuple[Any, ...],
) -> str:
    if parsed.problem_type.value == "integral":
        variable = parsed.variable or "x"
        expression = expression_to_latex(
            parsed.expression,
            local_dict=local_dict,
            transformations=transformations,
        )
        return f"\\int {expression}\\, d{variable}"

    if parsed.problem_type.value == "derivative":
        variable = parsed.variable or "x"
        expression = expression_to_latex(
            parsed.expression,
            local_dict=local_dict,
            transformations=transformations,
        )
        return f"\\frac{{d}}{{d{variable}}}\\left({expression}\\right)"

    if parsed.problem_type.value == "limit":
        variable = parsed.variable or "x"
        point = parsed.limit_point or "0"
        expression = expression_to_latex(
            parsed.expression,
            local_dict=local_dict,
            transformations=transformations,
        )
        return f"\\lim_{{{variable} \\to {point}}} {expression}"

    if parsed.problem_type.value == "equation" and "=" in parsed.expression:
        left, right = parsed.expression.split("=", maxsplit=1)
        return (
            f"{expression_to_latex(left, local_dict=local_dict, transformations=transformations)} = "
            f"{expression_to_latex(right, local_dict=local_dict, transformations=transformations)}"
        )

    return expression_to_latex(
        parsed.expression,
        local_dict=local_dict,
        transformations=transformations,
    )


def expression_to_latex(
    expression: str,
    *,
    local_dict: dict[str, Any],
    transformations: tuple[Any, ...],
) -> str:
    normalized = normalize_text(expression).strip()
    try:
        parsed_expression = parse_expr(
            normalized,
            local_dict=local_dict.copy(),
            transformations=transformations,
            evaluate=False,
        )
        return latex(parsed_expression)
    except Exception:
        fallback = normalized.replace("**", "^").replace("*", " ")
        fallback = re.sub(r"exp\(([^()]+)\)", r"e^{\1}", fallback)
        return fallback


def extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.endswith("```"):
        raw = raw[:-3]

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in practice response. Raw: {raw}")
    json_str = match.group(0)
    json_str = re.sub(r'\\(?=[^"\\/bfnrtu])', r"\\\\", json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse error: %s - Raw string: %s", exc, json_str)
        raise ValueError(f"Invalid JSON generated: {exc}") from exc
