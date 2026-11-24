"""CLI plumbing tests: the dictionary opt-in flags must reach the pipeline.

The library-level opt-in (document_year / use_dictionary) is useless if the
command line cannot express it, and the default -- dictionary guessing OFF --
must survive the trip from argparse into the pipeline call.
"""
import sys
from pathlib import Path

import pytest

from wecos_ocr import cli


class _FakeResult:
    def __init__(self, text: str = "မြန်မာစာ"):
        self.text = text


@pytest.fixture
def captured(monkeypatch, tmp_path):
    """Run cli.main() with a faked pipeline and capture the kwargs it receives."""
    calls: list[dict] = []

    def fake_transcribe(*args, **kwargs):
        calls.append(kwargs)
        return _FakeResult()

    def fake_convert_pdf(*args, **kwargs):
        calls.append(kwargs)
        return "# markdown"

    monkeypatch.setattr(cli, "transcribe", fake_transcribe)
    monkeypatch.setattr(cli, "convert_pdf_to_md", fake_convert_pdf)
    return calls


def _run(monkeypatch, argv: list[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["wecos-ocr", *argv])
    cli.main()


def test_image_defaults_to_no_dictionary_pass(monkeypatch, captured, tmp_path):
    """The default must not enable the modern-dictionary guesser."""
    image = tmp_path / "page.jpg"
    image.write_bytes(b"not-really-a-jpeg")

    _run(monkeypatch, ["image", str(image)])

    assert captured[0]["document_year"] is None
    assert captured[0]["use_dictionary"] is None


def test_image_document_year_reaches_the_pipeline(monkeypatch, captured, tmp_path):
    image = tmp_path / "page.jpg"
    image.write_bytes(b"not-really-a-jpeg")

    _run(monkeypatch, ["image", str(image), "--document-year", "1994"])

    assert captured[0]["document_year"] == 1994
    assert captured[0]["use_dictionary"] is None


def test_image_use_dictionary_flag_reaches_the_pipeline(monkeypatch, captured, tmp_path):
    image = tmp_path / "page.jpg"
    image.write_bytes(b"not-really-a-jpeg")

    _run(monkeypatch, ["image", str(image), "--use-dictionary"])

    assert captured[0]["use_dictionary"] is True
    assert captured[0]["document_year"] is None


def test_pdf_document_year_reaches_the_pipeline(monkeypatch, captured, tmp_path):
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.4")

    _run(monkeypatch, ["pdf", str(pdf), "--document-year", "2001"])

    assert captured[0]["document_year"] == 2001
