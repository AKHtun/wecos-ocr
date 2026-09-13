"""Abstract Base Class for OCR Inference Backends."""

from abc import ABC, abstractmethod
from typing import Optional
from PIL import Image


class BaseOCRBackend(ABC):
    """Abstract interface for multi-backend OCR engines."""

    @abstractmethod
    def ocr_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """Transcribe an in-memory PIL Image into clean Unicode text."""
        pass
