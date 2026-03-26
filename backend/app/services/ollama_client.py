from __future__ import annotations

import httpx
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import Settings


class OllamaClientError(RuntimeError):
    """Raised when the Ollama endpoint cannot be reached or returns an invalid response."""


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout_seconds

    def generate(self, *, system_prompt: str, prompt: str) -> str:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "system": system_prompt,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.2},
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaClientError("No fue posible comunicarse con Ollama.") from exc

        payload = response.json()
        generated_text = str(payload.get("response", "")).strip()
        if not generated_text:
            raise OllamaClientError("Ollama respondio sin contenido util.")
        return generated_text
