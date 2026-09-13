"""Hermetic Myanmar Orthography Guard & Lexical Repair Engine.

Ground-truth validation and OCR correction against the official Myanmar Language
Commission (MLC 2003) standard (မြန်မာစာလုံးပေါင်းသတ်ပုံကျမ်း).
"""

from __future__ import annotations

import importlib.resources
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .normalizer import clean_myanmar_canonical
from .syllable import segment_syllables

_logger = logging.getLogger("wecos_ocr.orthography")

# Common visual OCR character confusions in historical Myanmar script
_OCR_CONFUSION_PAIRS = [
    ('ခ', 'ဒ'), ('ဒ', 'ခ'),
    ('င', 'စ'), ('စ', 'င'),
    ('က', 'တ'), ('တ', 'က'),
    ('ပ', 'ယ'), ('ယ', 'ပ'),
    ('ဝ', '၀'), ('၀', 'ဝ'),  # Burmese Wa vs Burmese Zero
    ('ဉ', 'ည'), ('ည', 'ဉ'),
    ('စ', 'ခ'), ('ခ', 'စ'),
    ('ထ', 'ဒ'), ('ဒ', 'ထ'),
    ('ပ', 'ဎ'), ('ဎ', 'ပ'),
    ('ဓာ', 'စာ'), ('စာ', 'ဓာ'),
]

# Common OCR optical multi-char ligature corrections
_OCR_LIGATURE_FIXES = {
    'စျ': 'ဈ',
    'ဇက္ပဲ': 'ဇကွဲ',
    'ထက္ပြီး': 'ဏကြီး',
    'ဒထွေး': 'ဒဒွေး',
    'ခစွေး': 'ခခွေး',
    'ဓာကျက်': 'စာကျက်',
    'ပရေမှတ်': 'ဎရေမှုတ်',
    'ဒုရင်ကောက်': 'ဍရင်ကောက်',
    'ခုရင်ကောက်': 'ဍရင်ကောက်',
}

# Common monosyllabic Burmese verbs & basic words
_COMMON_BASE_WORDS: set[str] = {
    "တက်", "ဆင်း", "သွား", "လာ", "စား", "သောက်", "ဝတ်", "နေ", "ထိုင်", "အိပ်",
    "ရေး", "ဖတ်", "ကြည့်", "ပြော", "ဆို", "ယူ", "ပေး", "လုပ်", "ကိုင်", "စီး", "နင်း",
    "ချိတ်", "ဆွဲ", "ထူး", "ကောက်", "တက်မယ်", "ပူ",
}

# Spoken and literary Burmese grammatical & verbal particles
_GRAMMAR_PARTICLES: set[str] = {
    "၌", "၍", "၎င်း", "သော်", "လျှင်", "ဖြင့်", "သည်", "၏", "ကို", "က",
    "မှ", "တွင်", "နှင့်", "သို့", "ကြောင့်", "အား", "ကော", "လည်း",
    "ပင်", "သာ", "မူ", "တော့", "ပြီး", "လျက်", "ရက်", "စွာ",
    "တယ်", "မယ်", "တဲ့", "မဲ့", "ပါ", "ပြီ", "ဦး", "ဘူး", "လား", "လဲ",
    "နေ", "ထား", "ခဲ့", "ပေး", "ရ", "စေ", "ရုံ", "တောင်", "စမ်း", "ရမလား",
}


class MyanmarOrthographyGuard:
    """Ground-truth lexical validator and OCR spell repair using MLC 2003 standard."""

    def __init__(self, custom_words_path: Optional[Path] = None):
        self.words: Set[str] = set()
        self.max_word_len: int = 0
        self._loaded: bool = False
        self._load(custom_words_path)

    def _load(self, custom_path: Optional[Path] = None) -> None:
        """Load bundled or custom headword list."""
        try:
            if custom_path and custom_path.exists():
                lines = custom_path.read_text(encoding="utf-8").splitlines()
            else:
                # Load bundled package asset
                ref = importlib.resources.files("wecos_ocr.linguistics.data") / "mlc_words.txt"
                with ref.open("r", encoding="utf-8") as f:
                    lines = f.read().splitlines()

            for line in lines:
                w = unicodedata.normalize("NFC", line.strip())
                if w:
                    self.words.add(w)
                    if len(w) > self.max_word_len:
                        self.max_word_len = len(w)

            self.words.update(_COMMON_BASE_WORDS)
            self._loaded = True
            _logger.info("Loaded %d MLC orthography headwords", len(self.words))
        except Exception as exc:
            _logger.error("Failed to load orthography dictionary: %s", exc)

    def segment_maxmatch(self, text: str) -> List[str]:
        """Dictionary-guided Maximum Matching word tokenization with syllable fallback."""
        if not text:
            return []

        text = clean_myanmar_canonical(text.strip())
        tokens: List[str] = []
        n = len(text)
        i = 0

        while i < n:
            if text[i].isspace():
                tokens.append(text[i])
                i += 1
                continue

            matched = False
            end_limit = min(n, i + self.max_word_len)
            for j in range(end_limit, i + 1, -1):
                sub = text[i:j]
                if sub in self.words:
                    tokens.append(sub)
                    i = j
                    matched = True
                    break

            if not matched:
                remaining = text[i:]
                syls = segment_syllables(remaining)
                if syls:
                    next_unit = syls[0]
                    tokens.append(next_unit)
                    i += len(next_unit)
                else:
                    tokens.append(text[i])
                    i += 1

        return tokens

    def suggest_ocr_fixes(self, word: str, max_suggestions: int = 3) -> List[str]:
        """Suggest candidate correct spellings by swapping common OCR visual confusion pairs."""
        norm_word = clean_myanmar_canonical(word.strip())
        if norm_word in self.words:
            return [norm_word]

        candidates = set()
        if norm_word in _OCR_LIGATURE_FIXES:
            candidates.add(_OCR_LIGATURE_FIXES[norm_word])

        for char_idx, char in enumerate(norm_word):
            for orig, alt in _OCR_CONFUSION_PAIRS:
                if char == orig:
                    cand = norm_word[:char_idx] + alt + norm_word[char_idx + 1:]
                    if cand in self.words:
                        candidates.add(cand)

        return sorted(list(candidates))[:max_suggestions]

    def repair_ocr_text(self, text: str) -> tuple[str, dict[str, int]]:
        """Repair OCR text using dictionary-guided confusion-pair swapping and syllable validation."""
        if not self._loaded or not text.strip():
            return text, {"total_tokens": 0, "dict_hits": 0, "repairs": 0, "oov_tokens": 0}

        lines_out: list[str] = []
        total_tokens = 0
        dict_hits = 0
        repairs = 0
        oov_tokens = 0

        for line in text.splitlines():
            clean_line = clean_myanmar_canonical(line)
            # Normalize trailing punctuation noise
            clean_line = re.sub(r'[%#\'ႈ]+\s*$', '။', clean_line)

            for err, fix in _OCR_LIGATURE_FIXES.items():
                if err in clean_line:
                    clean_line = clean_line.replace(err, fix)
                    repairs += 1

            tokens = self.segment_maxmatch(clean_line)
            repaired_tokens: list[str] = []

            for tok in tokens:
                if tok.isspace() or tok in ("၊", "။", "-", "–"):
                    repaired_tokens.append(tok)
                    continue

                total_tokens += 1
                norm_tok = clean_myanmar_canonical(tok.strip())

                if norm_tok in self.words or norm_tok in _GRAMMAR_PARTICLES:
                    dict_hits += 1
                    repaired_tokens.append(tok)
                    continue

                fixes = self.suggest_ocr_fixes(norm_tok, max_suggestions=1)
                if fixes:
                    repaired_tokens.append(fixes[0])
                    repairs += 1
                else:
                    oov_tokens += 1
                    repaired_tokens.append(tok)

            lines_out.append("".join(repaired_tokens))

        telemetry = {
            "total_tokens": total_tokens,
            "dict_hits": dict_hits,
            "repairs": repairs,
            "oov_tokens": oov_tokens,
        }
        return "\n".join(lines_out), telemetry


_instance: Optional[MyanmarOrthographyGuard] = None

def get_myanmar_orthography_guard() -> MyanmarOrthographyGuard:
    global _instance
    if _instance is None:
        _instance = MyanmarOrthographyGuard()
    return _instance

def repair_ocr_spelling(text: str) -> tuple[str, dict[str, int]]:
    return get_myanmar_orthography_guard().repair_ocr_text(text)
