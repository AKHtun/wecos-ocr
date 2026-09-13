"""wecos-ocr: Sovereign Myanmar OCR, Epigraphical Decipherment & Syllable Engine.

Features:
- Adaptive scanned-plate contrast enhancement & de-yellowing
- Formal 12-category syllable segmentation FSA (Zin Maung Maung & Mikami 2008)
- MLC 2003 dictionary-guided orthographic repair
- Multi-backend neural inference (Ollama, PyTorch/Transformers, Tesseract, Cloud Vision)
"""

from .pipeline import OCRResult, convert_pdf_to_md, transcribe

__version__ = "0.1.0"
__author__ = "AKHtun"
__license__ = "Apache-2.0"

__all__ = [
    "transcribe",
    "convert_pdf_to_md",
    "OCRResult",
]

