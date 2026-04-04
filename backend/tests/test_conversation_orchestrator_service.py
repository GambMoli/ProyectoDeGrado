from types import SimpleNamespace

from app.schemas.enums import ChatMode
from app.services.conversation_orchestrator_service import ConversationOrchestratorService


class DirectReplyOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return (
            '{"mode":"direct","reply":"Vamos con el mismo ejercicio. '
            'Primero aplicamos la regla del producto y luego derivamos cada factor.",'
            '"reason":"continues current exercise","topic":"derivative",'
            '"detail_level":"detailed","confidence":0.91}'
        )


class ToolReplyOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return (
            '{"mode":"tool","actions":["generate_practice"],'
            '"reason":"wants a fresh exercise","topic":"integral",'
            '"detail_level":"auto","confidence":0.87}'
        )


def test_orchestrator_can_reply_directly_when_context_is_enough() -> None:
    service = ConversationOrchestratorService(
        settings=SimpleNamespace(),
        ollama_client=DirectReplyOllamaClient(),  # type: ignore[arg-type]
    )

    result = service.orchestrate(
        message="No supe resolverlo, podrias hacerme el paso por paso?",
        requested_mode=ChatMode.AUTO,
        conversation_context=["assistant: Deriva x^2*cos(x) usando la regla del producto."],
        agent_state={
            "pending_practice": {
                "topic": "derivative",
                "exercise_text": "Deriva x^2*cos(x).",
            }
        },
    )

    assert result is not None
    assert result.mode == "direct"
    assert "regla del producto" in (result.reply or "")


def test_orchestrator_can_request_a_tool_without_using_the_planner() -> None:
    service = ConversationOrchestratorService(
        settings=SimpleNamespace(),
        ollama_client=ToolReplyOllamaClient(),  # type: ignore[arg-type]
    )

    result = service.orchestrate(
        message="Dame un ejercicio nuevo de integrales",
        requested_mode=ChatMode.AUTO,
        conversation_context=[],
        agent_state={},
    )

    assert result is not None
    assert result.mode == "tool"
    assert result.actions == ["generate_practice"]
