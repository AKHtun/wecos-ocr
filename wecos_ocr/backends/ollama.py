"""Ollama / vLLM REST API Backend for Local VLM Inference."""

import base64
import io
import json
import urllib.request
from typing import Optional
from PIL import Image

from .base import BaseOCRBackend

DEFAULT_PROMPT = (
    "Transcribe the Myanmar text in this image accurately into clean Unicode text. "
    "Preserve line breaks, punctuation, and structural layout."
)


class OllamaBackend(BaseOCRBackend):
    """Backend for Ollama-hosted Vision-Language Models."""

    def __init__(
        self,
        model: str = "wecos-myanmar-ocr-qwen3:8b",
        endpoint: str = "http://127.0.0.1:11434",
        timeout: int = 120,
    ):
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout

    def ocr_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=95)
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        p = prompt or DEFAULT_PROMPT
        payload = json.dumps({
            "model": self.model,
            "prompt": p,
            "images": [img_b64],
            "stream": False,
            "options": {
                "temperature": 0.0,
                "repeat_penalty": 1.1,
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.endpoint}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
