"""End-to-End Transcription Pipeline & PDF Document Processing."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from PIL import Image

from .backends import BaseOCRBackend, OllamaBackend, TesseractBackend
from .linguistics import clean_myanmar_canonical, repair_ocr_spelling, segment_syllables
from .vision import enhance_scanned_plate, is_yellowed_or_low_contrast


@dataclass
class OCRResult:
    """Structured OCR transcription result."""
    text: str
    raw_text: str
    engine: str
    telemetry: Dict[str, Any] = field(default_factory=dict)
    syllables: List[str] = field(default_factory=list)


def _get_backend(name: str, **kwargs) -> BaseOCRBackend:
    name_lower = name.lower()
    if name_lower in ("ollama", "vllm"):
        return OllamaBackend(**kwargs)
    elif name_lower == "tesseract":
        return TesseractBackend(**kwargs)
    else:
        raise ValueError(f"Unknown OCR backend: {name}. Supported: 'ollama', 'tesseract'")


def transcribe(
    input_source: Union[str, Path, Image.Image],
    backend: Union[str, BaseOCRBackend] = "ollama",
    model: str = "wecos-myanmar-ocr-qwen3:8b",
    enhance: bool = True,
    repair: bool = True,
    prompt: Optional[str] = None,
    **backend_kwargs,
) -> OCRResult:
    """Transcribe a single image or image file into clean Myanmar Unicode text."""
    # 1. Load image
    if isinstance(input_source, (str, Path)):
        img = Image.open(input_source)
    elif isinstance(input_source, Image.Image):
        img = input_source
    else:
        raise TypeError(f"Unsupported input type: {type(input_source)}")

    # 2. Vision pre-processing
    enhanced_applied = False
    if enhance:
        if is_yellowed_or_low_contrast(img):
            img = enhance_scanned_plate(img)
            enhanced_applied = True

    # 3. Model inference
    if isinstance(backend, str):
        if backend == "ollama" and "model" not in backend_kwargs:
            backend_kwargs["model"] = model
        engine_instance = _get_backend(backend, **backend_kwargs)
        engine_name = backend
    else:
        engine_instance = backend
        engine_name = type(backend).__name__

    raw_text = engine_instance.ocr_image(img, prompt=prompt)

    # 4. Orthographic and syllable repair
    repaired_text = clean_myanmar_canonical(raw_text)
    telemetry: Dict[str, Any] = {"enhanced_vision": enhanced_applied}

    if repair:
        repaired_text, rep_telem = repair_ocr_spelling(repaired_text)
        telemetry.update(rep_telem)

    sylls = segment_syllables(repaired_text)

    return OCRResult(
        text=repaired_text,
        raw_text=raw_text,
        engine=engine_name,
        telemetry=telemetry,
        syllables=sylls,
    )


def convert_pdf_to_md(
    pdf_path: Union[str, Path],
    output_md: Optional[Union[str, Path]] = None,
    backend: str = "ollama",
    model: str = "wecos-myanmar-ocr-qwen3:8b",
    dpi: int = 150,
    enhance: bool = True,
    repair: bool = True,
) -> str:
    """Convert a multi-page PDF book into clean, assembled Markdown."""
    try:
        import fitz
    except ImportError:
        raise ImportError(
            "PyMuPDF is required for PDF conversion. "
            "Install with: pip install wecos-ocr[pdf] or pip install pymupdf"
        )

    pdf_p = Path(pdf_path)
    if not pdf_p.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_p}")

    doc = fitz.open(pdf_p)
    pages_md = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        res = transcribe(
            img,
            backend=backend,
            model=model,
            enhance=enhance,
            repair=repair,
        )
        pages_md.append(f"## Page {i + 1}\n\n{res.text}")

    full_md = "\n\n---\n\n".join(pages_md)

    if output_md:
        out_p = Path(output_md)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(full_md, encoding="utf-8")

    return full_md
