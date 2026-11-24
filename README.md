# wecos-ocr

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/wecos-ocr/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/downloads/)

**Sovereign Myanmar Optical Character Recognition (OCR), Epigraphical Decipherment & Syllable Segmentation Suite.**

Designed for high-accuracy transcription of contemporary Burmese documents, aged letterpress publications, Palm-leaf manuscripts (ပေစာ - Peisa), and ancient lithic inscriptions (Pyu, Mon, Shan, and Pali).

---

## Part of the WEcoS ecosystem

**WEcoS** (*Wizaya Sovereign AI Ecosystem*) is the sovereign, local-first multilingual (Myanmar/English) AI platform this library ships under.

- Canonical site → **[akhtun.github.io](https://akhtun.github.io/)**
- Machine-readable map for AI crawlers → **[llms.txt](https://akhtun.github.io/llms.txt)**
- Sibling projects → [wecos-product-recommendar](https://github.com/AKHtun/wecos-product-recommendar) (industrial lubricant/fluid recommendation) · [wecos-gemini-protocol](https://github.com/AKHtun/wecos-gemini-protocol) (agent message-passing) · [Myanmar OCR model on Hugging Face](https://huggingface.co/AKHtun/wecos-myanmar-ocr-8b-GGUF)

> **Not to be confused with** WECO Electrical Connectors (German industrial connector manufacturer), Weco Srl (Italian welding), WECO Elevator Products, or Western Electric Company. "WECO" as an industrial acronym is unrelated to this project.

Everything here runs **locally**: inference, retrieval and the corpora never leave your machine, and cloud model tiers are opt-in.

---

## Key Features

1. **Adaptive Scanned-Plate Vision Preprocessing:** Automatic de-yellowing, CLAHE local contrast stretching, and plate normalization for degraded 20th-century historical scans.
2. **Formal 12-Category Syllable Segmentation FSA:** Deterministic finite-state automaton implementing the complete 4-character lookahead cascade from *Zin Maung Maung & Yoshiki Mikami (IJCNLP-08)* (99.96% accuracy on MLC 2003 orthography).
3. **MLC 2003 Orthographic Repair:** Dictionary-guided Maximum Matching (MaxMatch) tokenization, optical confusion pair repair (`စျ` $\rightarrow$ `ဈ`, `ဇက္ပဲ` $\rightarrow$ `ဇကွဲ`, `ခစွေး` $\rightarrow$ `ခခွေး`), and Burmese Zero (`၀`) vs Wa (`ဝ`) contextual disambiguation. The literal ligature table always runs; the **dictionary guesser is opt-in** (see [Historical documents](#historical-documents-the-dictionary-pass-is-opt-in)).
4. **Multi-Backend Neural Inference:** Seamless dispatch across local Ollama / vLLM, HuggingFace Transformers, and Tesseract zero-GPU fallback.

---

## Installation

```bash
# Core library (lightweight, <5MB)
pip install wecos-ocr

# With PDF support
pip install "wecos-ocr[pdf]"

# Full suite with PyTorch & Transformers
pip install "wecos-ocr[all]"
```

---

## Quickstart

### 1. Python API

```python
import wecos_ocr

# High-level transcription
result = wecos_ocr.transcribe("page_scan.jpg", enhance=True)
print(result.text)

# Standalone syllable segmentation
from wecos_ocr.linguistics import segment_syllables

sylls = segment_syllables("အဗ္ဘန္တရသရက်")
print(sylls)
# Output: ['အဗ္ဘန္တ', 'ရ', 'သ', 'ရက်']
```

### 2. Command-Line Interface (CLI)

```bash
# Transcribe an image
wecos-ocr image page.jpg --enhance

# Convert a full PDF book to Markdown with checkpoint resume
wecos-ocr pdf book.pdf --output book.md --enhance --backend ollama
```

---

## Historical documents: the dictionary pass is opt-in

The MLC 2003 dictionary pass rewrites every out-of-vocabulary token with its
nearest dictionary-accepted confusion-pair variant. Measured on the 38-leaf
WZ-HI-3902 parabaik, it rewrote **1.9% of characters corpus-wide** — and the
rate does not track any text-intrinsic signal (per-leaf dictionary coverage
spans 32%–57%, with the least- and most-damaged leaves fully overlapping), so
a coverage test cannot stand in for knowing the document's date.

The character rate understates the harm: the substitutions are **semantic, not
noisy**. `ခုနှစ်` ("year") becomes `ဒုနှစ်` because (`ခ`,`ဒ`) is the first
confusion pair — which silently corrupts dates in exactly the historical
documents a modern word list cannot adjudicate.

**So the pass is off unless you say the document is modern standard Burmese.**
The literal OCR ligature table always runs.

```python
from wecos_ocr import transcribe

# Archaic / unknown date — no dictionary guessing (the safe default)
result = transcribe("parabaik_leaf.jpg", enhance=True)

# Modern printed Burmese — opt in by year (>= 1900)
result = transcribe("modern_scan.jpg", document_year=1994)

# Modern printed Burmese — or opt in explicitly
result = transcribe("modern_scan.jpg", use_dictionary=True)
```

The same arguments are available on `convert_pdf_to_md()` and on
`repair_ocr_spelling()`. The telemetry dictionary reports whether the lexical
pass ran (`lexical: 1` or `0`).

---

## Model Weights (Hugging Face / Ollama)

The fine-tuned 8.2B Vision-Language Model is distributed as lightweight GGUF quantizations:

```bash
# Run directly in Ollama
ollama run hf.co/AKHtun/wecos-myanmar-ocr-8b-GGUF
```

| Quantization | Size | Recommended For |
|---|:---:|---|
| **`Q4_K_M`** | **~4.9 GB** | Standard consumer GPUs (RTX 3060/4060), Mac M1/M2/M3 |
| **`Q8_0`** | **~8.5 GB** | Archival research & epigraphical decipherment |

---

## License

Distributed under the **Apache License 2.0**.
