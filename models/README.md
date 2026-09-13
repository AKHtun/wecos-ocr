---
license: apache-2.0
language:
- my
- pli
tags:
- ocr
- vision
- multimodal
- myanmar
- burmese
- epigraphy
- peisa
- pali
- gguf
- ollama
base_model: Qwen/Qwen2.5-VL-7B-Instruct
pipeline_tag: image-to-text
---

# WEcoS Myanmar OCR 8B (GGUF)

**Sovereign Vision-Language Model specialized in Optical Character Recognition (OCR) for contemporary Burmese, Pali literature, Palm-leaf manuscripts (ပေစာ), and ancient epigraphical inscriptions (Pyu, Mon, Shan).**

Developed by **AKHtun**.

---

## Model Description

`wecos-myanmar-ocr-8b` is an 8.2-billion parameter multimodal Vision-Language Model optimized to decipher complex Myanmar writing systems where standard OCR engines fail:
* **Complex Subjoined Consonants:** Accurately decodes vertical consonant stacks ($C + S + C$, e.g. `သမ္မတ`, `ဝတ္ထု`, `မင်္ဂလာ`).
* **Ancient Epigraphy & Palm-Leaf:** Transcribes ancient lithic inscriptions, finger-marked votive tablets, and palm-leaf manuscripts (Peisa).
* **Aged & Low-Contrast Scans:** Robust against 20th-century yellowed paper, letterpress ink-spread, and low-contrast photographic plates.
* **Pali Nissaya:** Accurately parses interlinear Pali-Burmese bilingual texts with rare diacritics.

---

## Quantization Formats Available

| File | Size | VRAM Required | Intended Audience |
|---|:---:|:---:|---|
| `wecos-myanmar-ocr-8b-Q4_K_M.gguf` | **~4.9 GB** | 6GB – 8GB | **Recommended:** Standard laptops, RTX 3060/4060, Mac M1/M2/M3 |
| `wecos-myanmar-ocr-8b-Q8_0.gguf` | **~8.5 GB** | 12GB – 16GB | Archival researchers, epigraphists, digital libraries |
| `mmproj-wecos-ocr-f16.gguf` | **~1.16 GB** | — | Required vision projector for multimodal inference |

---

## Quickstart with Ollama

You can run this model directly via Ollama without manual conversion:

```bash
# Pull and run directly from Hugging Face
ollama run hf.co/AKHtun/wecos-myanmar-ocr-8b-GGUF
```

Or assemble locally using the included `Modelfile`:

```bash
ollama create wecos-myanmar-ocr:8b -f Modelfile
ollama run wecos-myanmar-ocr:8b
```

---

## Using with `wecos-ocr` Python Library

```python
import wecos_ocr

# Automatic vision enhancement + VLM inference + MLC 2003 orthography repair
result = wecos_ocr.transcribe("ancient_inscription.jpg", enhance=True)
print(result.text)
```

---

## Prompt Template

```text
<|im_start|>system
You are WEcoS Myanmar OCR, an expert optical character recognition system specialized in contemporary Myanmar script, Pali literature, and historical inscriptions. Transcribe all text accurately in Unicode NFC.<|im_end|>
<|im_start|>user
<image>
Transcribe the Myanmar text in this image accurately into clean Unicode text. Preserve line breaks, punctuation, and structural layout.<|im_end|>
<|im_start|>assistant
```

---

## License

This model and its associated weights are distributed under the **Apache License 2.0**.
