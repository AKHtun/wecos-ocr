"""wecos_ocr.backends: Multi-backend abstraction for local and cloud OCR models."""

from .base import BaseOCRBackend
from .ollama import OllamaBackend
from .tesseract import TesseractBackend

__all__ = ["BaseOCRBackend", "OllamaBackend", "TesseractBackend"]
