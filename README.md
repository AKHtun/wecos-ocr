# wecos-ocr

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/wecos-ocr/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/downloads/)

**Sovereign Myanmar Optical Character Recognition (OCR), Epigraphical Decipherment & Syllable Segmentation Suite.**

Designed for high-accuracy transcription of contemporary Burmese documents, aged letterpress publications, Palm-leaf manuscripts (ပေစာ - Peisa), and ancient lithic inscriptions (Pyu, Mon, Shan, and Pali).

---

## Key Features

1. **Adaptive Scanned-Plate Vision Preprocessing:** Automatic de-yellowing, CLAHE local contrast stretching, and plate normalization for degraded 20th-century historical scans.
2. **Formal 12-Category Syllable Segmentation FSA:** Deterministic finite-state automaton implementing the complete 4-character lookahead cascade from *Zin Maung Maung & Yoshiki Mikami (IJCNLP-08)* (99.96% accuracy on MLC 2003 orthography).
3. **MLC 2003 Orthographic Repair:** Dictionary-guided Maximum Matching (MaxMatch) tokenization, optical confusion pair repair (`စျ` $\rightarrow$ `ဈ`, `ဇက္ပဲ` $\rightarrow$ `ဇကွဲ`, `ခစွေး` $\rightarrow$ `ခခွေး`), and Burmese Zero (`၀`) vs Wa (`ဝ`) contextual disambiguation.
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
