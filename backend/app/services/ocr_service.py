from __future__ import annotations

import io
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from PIL import Image, ImageOps

from app.core.config import Settings
from app.utils.expression_normalizer import (
    extract_candidate_segment,
    looks_like_structured_math,
    normalize_text,
)

logger = logging.getLogger(__name__)


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
        image_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OCRExtractionResult:
        raise NotImplementedError


class MockOCRService(OCRService):
    provider_name = "mock"

    def extract_text(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OCRExtractionResult:
        return OCRExtractionResult(
            success=False,
            text=None,
            provider=self.provider_name,
            error_message=(
                "El OCR no esta configurado. Activa Tesseract o ingresa el "
                "ejercicio manualmente en el chat."
            ),
        )


class TesseractOCRService(OCRService):
    provider_name = "tesseract"

    def __init__(self, language: str = "eng", tesseract_cmd: str | None = None) -> None:
        self.language = language
        self.tesseract_cmd = tesseract_cmd

    def extract_text(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> OCRExtractionResult:
        try:
            import pytesseract
        except ImportError:
            logger.warning("pytesseract is not installed; falling back to OCR failure.")
            return OCRExtractionResult(
                success=False,
                text=None,
                provider=self.provider_name,
                error_message=(
                    "No se encontro la dependencia de OCR. "
                    "Prueba con una foto mas nitida o escribe el ejercicio manualmente."
                ),
            )

        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        try:
            image = Image.open(io.BytesIO(image_bytes))
            image = ImageOps.exif_transpose(image).convert("L")
            image = ImageOps.autocontrast(image)
            image = ImageOps.posterize(image.convert("RGB"), 2).convert("L")
            raw_text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config="--psm 6",
            )
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                config="--psm 6",
                output_type=pytesseract.Output.DICT,
            )
            cleaned_text = normalize_text(raw_text)
            confidence = self._average_confidence(data)
            candidate = extract_candidate_segment(cleaned_text)
            if cleaned_text.strip():
                if not looks_like_structured_math(candidate):
                    return OCRExtractionResult(
                        success=False,
                        text=None,
                        provider=self.provider_name,
                        raw_text=raw_text,
                        confidence=confidence,
                        error_message=(
                            "La imagen no se pudo leer como un ejercicio matematico con suficiente claridad. "
                            "Intenta con una foto mas nitida, mejor encuadrada o escribe el ejercicio manualmente."
                        ),
                    )

                if confidence is not None and confidence < 35:
                    return OCRExtractionResult(
                        success=False,
                        text=None,
                        provider=self.provider_name,
                        raw_text=raw_text,
                        confidence=confidence,
                        error_message=(
                            "La imagen se leyo con muy poca confianza. "
                            "Prueba con mejor iluminacion, una foto mas recta o escribe el ejercicio manualmente."
                        ),
                    )

                return OCRExtractionResult(
                    success=True,
                    text=cleaned_text,
                    provider=self.provider_name,
                    raw_text=raw_text,
                    confidence=confidence,
                )

            return OCRExtractionResult(
                success=False,
                text=None,
                provider=self.provider_name,
                raw_text=raw_text,
                confidence=confidence,
                error_message=(
                    "No pude leer el ejercicio de la imagen. "
                    "Prueba con una foto mas nitida o escribe el enunciado manualmente."
                ),
            )
        except Exception as exc:
            logger.warning("OCR extraction failed for %s: %s", filename, exc)
            return OCRExtractionResult(
                success=False,
                text=None,
                provider=self.provider_name,
                error_message=(
                    "Hubo un problema procesando la imagen. "
                    "Prueba con otra foto o usa la entrada de texto."
                ),
            )

    @staticmethod
    def _average_confidence(data: dict[str, list[str]]) -> float | None:
        raw_confidences = data.get("conf", [])
        values: list[float] = []
        for raw_confidence in raw_confidences:
            try:
                value = float(raw_confidence)
            except (TypeError, ValueError):
                continue
            if value >= 0:
                values.append(value)
        if not values:
            return None
        return sum(values) / len(values)


def build_ocr_service(settings: Settings) -> OCRService:
    provider = settings.ocr_provider.lower().strip()
    if provider == "tesseract":
        return TesseractOCRService(
            language=settings.ocr_language,
            tesseract_cmd=settings.tesseract_cmd,
        )
    return MockOCRService()
