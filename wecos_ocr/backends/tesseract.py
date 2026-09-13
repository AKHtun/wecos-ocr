"""Tesseract OCR Backend for Zero-GPU CPU Fallback."""

import shutil
from typing import Optional
from PIL import Image

from .base import BaseOCRBackend


class TesseractBackend(BaseOCRBackend):
    """Fallback backend using Tesseract with Myanmar traineddata."""

    def __init__(self, lang: str = "mya", tesseract_cmd: Optional[str] = None):
        self.lang = lang
        self.tesseract_cmd = tesseract_cmd

    def ocr_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        try:
            import pytesseract
        except ImportError:
            raise ImportError(
                "pytesseract is required for Tesseract backend. "
                "Install with: pip install wecos-ocr[all] or pip install pytesseract"
            )

        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        elif shutil.which("tesseract") is None:
            # Common Windows default path fallback
            import os
            prog_files = os.environ.get("ProgramFiles", "")
            if prog_files:
                win_default = os.path.join(prog_files, "Tesseract-OCR", "tesseract.exe")
                if os.path.exists(win_default):
                    pytesseract.pytesseract.tesseract_cmd = win_default

        text = pytesseract.image_to_string(image, lang=self.lang)
        return text.strip()
