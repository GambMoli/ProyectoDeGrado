from types import SimpleNamespace

from app.services.response_composer_service import ResponseComposerService


class GoodComposerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return (
            "La derivada mide la tasa de cambio instantanea de una funcion. "
            "Para practicar, trabaja literalmente este ejercicio: "
            "Deriva la funcion f(x) = 4*x^3 - x + 6. "
            "Si te atoras, usa la regla de la potencia termino a termino."
        )


class LooseComposerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return "La derivada mide el cambio. Ahora intenta una funcion polinomica parecida."


def test_composer_uses_ollama_when_it_keeps_exact_exercise() -> None:
    service = ResponseComposerService(
        settings=SimpleNamespace(),
        ollama_client=GoodComposerOllamaClient(),  # type: ignore[arg-type]
    )

    composed = service.compose_guidance(
        user_message="Dime que sabes de derivadas y proponme un ejercicio",
        conversation_context=[],
        theory_text="La derivada mide la tasa de cambio instantanea de una funcion.",
        exercise_text="Deriva la funcion f(x) = 4*x^3 - x + 6.",
        hint="Aplica la regla de la potencia termino a termino.",
    )

    assert composed.source == "ollama_composer"
    assert "Deriva la funcion f(x) = 4*x^3 - x + 6." in composed.text


def test_composer_falls_back_when_llm_does_not_keep_exact_exercise() -> None:
    service = ResponseComposerService(
        settings=SimpleNamespace(),
        ollama_client=LooseComposerOllamaClient(),  # type: ignore[arg-type]
    )

    composed = service.compose_guidance(
        user_message="Dime que sabes de derivadas y proponme un ejercicio",
        conversation_context=[],
        theory_text="La derivada mide la tasa de cambio instantanea de una funcion.",
        exercise_text="Deriva la funcion f(x) = 4*x^3 - x + 6.",
        hint="Aplica la regla de la potencia termino a termino.",
    )

    assert composed.source == "fallback_exact_exercise"
    assert "Deriva la funcion f(x) = 4*x^3 - x + 6." in composed.text
