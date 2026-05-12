from __future__ import annotations

import io
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from PIL import Image

from app.core.config import Settings

logger = logging.getLogger(__name__)

_GEMINI_PROMPT = (
    "Eres una herramienta de OCR matematico. Tu UNICA funcion es transcribir exactamente lo "
    "que esta escrito en las imagenes. NO corrijas errores, NO completes pasos faltantes, NO "
    "sugieras correcciones, NO agregues pasos que no esten en la imagen. Si el estudiante "
    "cometio un error matematico, transcribelo tal como esta escrito.\n\n"
    "Se te envia {n} imagen(es) con un ejercicio matematico resuelto por un estudiante. "
    "Cada imagen puede contener uno o varios pasos del desarrollo.\n\n"
    "Tu tarea:\n"
    "1. Lee cada imagen en el orden dado.\n"
    "2. Transcribe CADA paso en LaTeX, respetando el orden visual de arriba a abajo.\n"
    "3. Transcribe EXACTAMENTE lo que ves, incluyendo errores.\n\n"
    "Devuelve UNICAMENTE el LaTeX de todos los pasos en una sola linea, donde cada paso este "
    "envuelto en el delimitador $$PASO$$ de esta forma: $$paso1$$ $$paso2$$ $$paso3$$ "
    "Sin saltos de linea, sin explicaciones, sin bloques de codigo.\n\n"
    "Ejemplo de respuesta:\n"
    "$$\\int x^2 dx$$ $$= \\frac{{x^3}}{{3}} + C$$"
)

_GEMINI_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
]


@dataclass(slots=True)
class OCRExtractionResult:
    success: bool
    text: str | None
    provider: str
    error_message: str | None = None
    raw_text: str | None = None
    confidence: float | None = None


class OCRService(ABC):
    provider_name = "base"

    @abstractmethod
    def extract_text(
        self,
        *,
        images: list[tuple[bytes, str, str]],
    ) -> OCRExtractionResult:
        raise NotImplementedError


class MockOCRService(OCRService):
    provider_name = "mock"

    def extract_text(
        self,
        *,
        images: list[tuple[bytes, str, str]],  # noqa: ARG002
    ) -> OCRExtractionResult:
        return OCRExtractionResult(
            success=False,
            text=None,
            provider=self.provider_name,
            error_message=(
                "El OCR no esta configurado. Activa Gemini o ingresa el "
                "ejercicio manualmente en el chat."
            ),
        )


def _is_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(k in msg for k in ("quota", "rate", "429", "resource_exhausted", "too many"))


class GeminiOCRService(OCRService):
    provider_name = "gemini"

    def __init__(self, api_keys: list[str]) -> None:
        from google import genai

        self._clients = [genai.Client(api_key=k) for k in api_keys]

    def extract_text(
        self,
        *,
        images: list[tuple[bytes, str, str]],
    ) -> OCRExtractionResult:
        first_filename = images[0][1] if images else "image"
        try:
            from google.genai import types

            parts: list = [_GEMINI_PROMPT.format(n=len(images))]
            for i, (image_bytes, _, _) in enumerate(images, start=1):
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                parts.append(f"Imagen {i}:")
                parts.append(types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png"))

            last_error: Exception | None = None
            for client_idx, client in enumerate(self._clients):
                for model in _GEMINI_MODELS:
                    try:
                        response = client.models.generate_content(
                            model=model,
                            contents=parts,
                        )
                        raw = (response.text or "").strip()
                        if raw:
                            return OCRExtractionResult(
                                success=True,
                                text=raw,
                                provider=self.provider_name,
                                raw_text=raw,
                                confidence=100.0,
                            )
                        return OCRExtractionResult(
                            success=False,
                            text=None,
                            provider=self.provider_name,
                            error_message=(
                                "No pude leer el ejercicio de la imagen. "
                                "Prueba con una foto mas nitida o escribe el enunciado manualmente."
                            ),
                        )
                    except Exception as exc:
                        last_error = exc
                        if _is_quota_error(exc):
                            logger.warning(
                                "[GeminiOCR] key %d modelo %s: cuota agotada, rotando clave.",
                                client_idx + 1, model,
                            )
                            break  # prueba la siguiente clave
                        logger.warning("[GeminiOCR] key %d modelo %s fallo: %s", client_idx + 1, model, exc)

            return OCRExtractionResult(
                success=False,
                text=None,
                provider=self.provider_name,
                error_message=(
                    f"Hubo un error en el servicio OCR: {last_error}. "
                    "Intenta de nuevo o escribe el ejercicio manualmente."
                ),
            )

        except Exception as exc:
            logger.warning("[GeminiOCR] error procesando %s: %s", first_filename, exc)
            return OCRExtractionResult(
                success=False,
                text=None,
                provider=self.provider_name,
                error_message=(
                    "Hubo un problema procesando la imagen. "
                    "Prueba con otra foto o usa la entrada de texto."
                ),
            )


def build_ocr_service(settings: Settings) -> OCRService:
    if not settings.gemini_api_keys:
        logger.warning("GEMINI_API_KEYS no esta configurada; usando MockOCRService.")
        return MockOCRService()
    return GeminiOCRService(api_keys=settings.gemini_api_keys)
