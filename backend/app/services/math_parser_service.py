from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.schemas.enums import ProblemType
from app.utils.expression_normalizer import extract_candidate_segment, looks_like_structured_math, normalize_text


class MathParserError(ValueError):
    def __init__(self, user_message: str, *, code: str = "parse_error") -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.code = code


@dataclass(slots=True)
class ParsedExercise:
    raw_input: str
    problem_type: ProblemType
    expression: str
    variable: str | None = None
    limit_point: str | None = None
    notes: list[str] = field(default_factory=list)


class MathParserService:
    _integral_keywords = re.compile("\\b(integral|integra|integrate|\u222b)\\b", re.IGNORECASE)
    _derivative_keywords = re.compile(
        "\\b(derivada|derivative|deriva|d/d[a-zA-Z])\\b",
        re.IGNORECASE,
    )
    _limit_keywords = re.compile("\\b(limite|l\\u00edmite|limit|lim)\\b", re.IGNORECASE)
    _limit_context_keywords = re.compile(
        "(?i)\\b(?:cuando|when)\\s+[a-zA-Z]\\s+(?:tiende\\s+a|tends\\s+to)\\s+[-+*/\\w().]+"
    )
    _simplify_keywords = re.compile("\\b(simplifica|simplify|reduce)\\b", re.IGNORECASE)
    _equation_keywords = re.compile("\\b(ecuacion|ecuaci\\u00f3n|equation|solve|resuelve)\\b", re.IGNORECASE)
    _leading_instruction_words = re.compile(
        "(?i)^(?:(?:resuelve|solve|calcula(?:r)?|evaluate|evalua|evaluar|halla|encuentra|determina|obt[e\u00e9]n|obten|simplifica|reduce|muestra)\\b[\\s,:;-]*)+"
    )
    _leading_context_words = re.compile(
        "(?i)^(?:(?:de|del|la|el|los|las|funcion|funci\\u00f3n|expresion|expresi\\u00f3n|valor|ejercicio|problema)\\b[\\s,:;-]*)+"
    )
    _leading_ocr_letters = re.compile(
        "^(?:[A-Za-z]\\s+){4,}(?=(?:\\d|\\(|sin\\b|cos\\b|tan\\b|log\\b|ln\\b|sqrt\\b|exp\\b|pi\\b|[xyztnabc]))"
    )
    _trailing_limit_context = re.compile(
        "(?i)\\s+cuando\\s+[a-zA-Z]\\s+tiende\\s+a\\s+[-+*/\\w().]+\\s*$"
    )
    _non_math_words = re.compile("\\b([A-Za-z]{2,})\\b")
    _allowed_math_words = {
        "sin",
        "cos",
        "tan",
        "log",
        "ln",
        "sqrt",
        "exp",
        "pi",
        "oo",
        "integral",
        "lim",
        "limit",
    }

    def parse(self, raw_text: str) -> ParsedExercise:
        normalized = normalize_text(raw_text)
        candidate = normalize_text(extract_candidate_segment(raw_text))
        problem_type = self._detect_problem_type(normalized, candidate)

        if problem_type == ProblemType.INTEGRAL:
            return self._parse_integral(candidate, normalized)
        if problem_type == ProblemType.DERIVATIVE:
            return self._parse_derivative(candidate, normalized)
        if problem_type == ProblemType.LIMIT:
            return self._parse_limit(candidate, normalized)
        if problem_type == ProblemType.EQUATION:
            return self._parse_equation(candidate, normalized)
        return self._parse_simplification(candidate, normalized)

    def _detect_problem_type(self, normalized: str, candidate: str) -> ProblemType:
        lowered = normalized.lower()
        if self._derivative_keywords.search(lowered) or re.search(r"d\s*/\s*d[a-zA-Z]", candidate, re.IGNORECASE):
            return ProblemType.DERIVATIVE
        if self._integral_keywords.search(lowered) or re.search(r"\s*d[a-zA-Z]\s*$", candidate):
            return ProblemType.INTEGRAL
        if self._limit_keywords.search(lowered) or self._limit_context_keywords.search(lowered) or "->" in candidate:
            return ProblemType.LIMIT
        if "=" in candidate or self._equation_keywords.search(lowered):
            return ProblemType.EQUATION
        if self._simplify_keywords.search(lowered):
            return ProblemType.SIMPLIFICATION
        if looks_like_structured_math(candidate):
            return ProblemType.SIMPLIFICATION
        raise MathParserError(
            "No detecte un ejercicio matematico claro.",
            code="no_clear_exercise",
        )

    def _parse_integral(self, candidate: str, normalized: str) -> ParsedExercise:
        notes = ["Se detecto una integral a partir del texto."]
        expression = candidate
        expression = re.sub("(?i)^.*?(integral|\u222b)\\s*(de|of)?\\s*", "", expression).strip()
        expression = expression.lstrip(":").strip()

        variable = None
        diff_match = re.search(r"(?P<expr>.+?)\s*d(?P<var>[a-zA-Z])\s*$", expression)
        if diff_match:
            expression = diff_match.group("expr").strip()
            variable = diff_match.group("var")
            notes.append(f"Se tomo {variable} como variable de integracion.")

        variable_match = re.search(
            "(?i)(?:respecto a|with respect to)\\s+(?P<var>[a-zA-Z])",
            normalized,
        )
        if variable_match and not variable:
            variable = variable_match.group("var")
            notes.append(f"Se tomo {variable} como variable de integracion por el contexto.")

        expression = self._cleanup_expression(expression)
        self._ensure_expression(expression)
        return ParsedExercise(
            raw_input=normalized,
            problem_type=ProblemType.INTEGRAL,
            expression=expression,
            variable=variable,
            notes=notes,
        )

    def _parse_derivative(self, candidate: str, normalized: str) -> ParsedExercise:
        notes = ["Se detecto una derivada en el enunciado."]
        variable = None
        expression = candidate

        shorthand_match = re.search(
            "(?i)d\\s*/\\s*d(?P<var>[a-zA-Z])\\s*(?P<expr>.+)",
            expression,
        )
        if shorthand_match:
            variable = shorthand_match.group("var")
            expression = shorthand_match.group("expr")
            notes.append(f"Se detecto la notacion d/d{variable}.")
        else:
            expression = re.sub(
                "(?i)^.*?(derivada|derivative|deriva)\\s*(de|of)?\\s*",
                "",
                expression,
            ).strip()

        variable_match = re.search(
            "(?i)(?:respecto a|with respect to)\\s+(?P<var>[a-zA-Z])",
            normalized,
        )
        if variable_match and not variable:
            variable = variable_match.group("var")
            notes.append(f"Se tomo {variable} como variable de derivacion.")

        expression = re.sub(
            "(?i)\\s*(respecto a|with respect to)\\s+[a-zA-Z]\\s*$",
            "",
            expression,
        ).strip()
        expression = self._cleanup_expression(expression)
        self._ensure_expression(expression)
        return ParsedExercise(
            raw_input=normalized,
            problem_type=ProblemType.DERIVATIVE,
            expression=expression,
            variable=variable,
            notes=notes,
        )

    def _parse_limit(self, candidate: str, normalized: str) -> ParsedExercise:
        notes = ["Se detecto un limite."]
        expression = candidate
        variable = None
        point = None

        arrow_match = re.search(
            "(?i)(?:.*?\\blim(?:ite|it)?\\b\\s*)?(?P<var>[a-zA-Z])\\s*->\\s*(?P<point>[-+*/\\w().]+)\\s*(?:[:,]?\\s*)?(?:de\\s+)?(?P<expr>.+)$",
            normalized,
        )
        if arrow_match:
            variable = arrow_match.group("var")
            point = arrow_match.group("point").strip(",:;")
            expression = arrow_match.group("expr")
            notes.append(f"Se detecto el limite cuando {variable} tiende a {point}.")
        else:
            text_match = re.search(
                "(?i)cuando\\s+(?P<var>[a-zA-Z])\\s+tiende\\s+a\\s+(?P<point>[-+*/\\w().]+)\\s*(?:[:,]?\\s*)?(?:de\\s+)?(?P<expr>.+)$",
                normalized,
            )
            if text_match:
                variable = text_match.group("var")
                point = text_match.group("point").strip(",:;")
                expression = text_match.group("expr")
                notes.append(f"Se detecto el limite cuando {variable} tiende a {point}.")
            else:
                reverse_match = re.search(
                    "(?i)(?P<expr>.+?)\\s+cuando\\s+(?P<var>[a-zA-Z])\\s+tiende\\s+a\\s+(?P<point>[-+*/\\w().]+)\\s*$",
                    normalized,
                )
                if reverse_match:
                    variable = reverse_match.group("var")
                    point = reverse_match.group("point").strip(",:;")
                    expression = reverse_match.group("expr")
                    notes.append(f"Se detecto el limite cuando {variable} tiende a {point}.")

        expression = re.sub("(?i)^.*?\\blim(?:ite|it)?\\b\\s*", "", expression).strip()
        expression = self._cleanup_expression(expression)
        self._ensure_expression(expression)

        if not variable or not point:
            raise MathParserError(
                "Pude detectar un limite, pero me falta el punto o la variable. Usa un formato como 'lim x->0 sin(x)/x'.",
                code="missing_limit_data",
            )

        return ParsedExercise(
            raw_input=normalized,
            problem_type=ProblemType.LIMIT,
            expression=expression,
            variable=variable,
            limit_point=point,
            notes=notes,
        )

    def _parse_equation(self, candidate: str, normalized: str) -> ParsedExercise:
        notes = ["Se detecto una ecuacion o una solicitud de resolver."]
        equation_match = re.search(
            r"(?P<eq>[A-Za-z0-9\(\)\+\-\*/\^\.,\s]+=[A-Za-z0-9\(\)\+\-\*/\^\.,\s]+)",
            candidate,
        )
        expression = equation_match.group("eq").strip() if equation_match else candidate.strip()
        expression = re.sub(
            "(?i)^.*?(ecuacion|ecuaci\\u00f3n|equation|solve|resuelve)\\s*(de|of|:)?\\s*",
            "",
            expression,
        ).strip()
        expression = self._cleanup_expression(expression)
        self._ensure_expression(expression)

        variable_match = re.search(
            "(?i)(?:para|for)\\s+(?P<var>[a-zA-Z])",
            normalized,
        )
        variable = variable_match.group("var") if variable_match else None
        return ParsedExercise(
            raw_input=normalized,
            problem_type=ProblemType.EQUATION,
            expression=expression,
            variable=variable,
            notes=notes,
        )

    def _parse_simplification(self, candidate: str, normalized: str) -> ParsedExercise:
        notes = ["No se detecto un operador avanzado; se intentara simplificar la expresion."]
        expression = candidate
        expression = re.sub(
            "(?i)^.*?(simplifica|simplify|reduce)\\s*(de|of|:)?\\s*",
            "",
            expression,
        ).strip()
        expression = self._cleanup_expression(expression)
        self._ensure_expression(expression)
        return ParsedExercise(
            raw_input=normalized,
            problem_type=ProblemType.SIMPLIFICATION,
            expression=expression,
            notes=notes,
        )

    @classmethod
    def _cleanup_expression(cls, expression: str) -> str:
        cleaned = normalize_text(expression).strip().strip(" ?!.,;:")
        cleaned = cleaned.replace("\u222b", "")
        cleaned = cls._leading_ocr_letters.sub("", cleaned).strip()

        previous = None
        while previous != cleaned:
            previous = cleaned
            cleaned = cls._leading_instruction_words.sub("", cleaned).strip()
            cleaned = cls._leading_context_words.sub("", cleaned).strip()

        cleaned = cls._trailing_limit_context.sub("", cleaned).strip()
        cleaned = cls._strip_non_math_words(cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip(" ?!.,;:")

    @classmethod
    def _strip_non_math_words(cls, expression: str) -> str:
        def replace_word(match: re.Match[str]) -> str:
            token = match.group(1)
            lowered = token.lower()
            if lowered in cls._allowed_math_words or len(token) == 1:
                return token
            return ""

        return cls._non_math_words.sub(replace_word, expression)

    @staticmethod
    def _ensure_expression(expression: str) -> None:
        if not expression or not looks_like_structured_math(expression):
            raise MathParserError(
                "No pude extraer una expresion matematica valida. Intenta escribir el ejercicio de forma mas directa.",
                code="invalid_expression",
            )
