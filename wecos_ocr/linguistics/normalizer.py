"""Myanmar Orthographic & Canonical Normalizer.

Disambiguates optical and typographical confusions, notably:
- Burmese digit Zero (၀, U+1040) vs consonant Wa (ဝ, U+1015) based on phonotactic environment.
- Unicode NFC normalization.
"""

import unicodedata

_CONSONANTS_ORD = set(range(0x1000, 0x1022)) | {0x103F}  # က..အ, ဿ
_VOWELS_MEDIALS_SIGNS_ORD = (
    set(range(0x102B, 0x1039)) |   # Dependent vowels, medials, F signs
    set(range(0x103A, 0x103F))     # Asat, Medials
)


def clean_myanmar_canonical(text: str) -> str:
    """Pre-clean text into Unicode NFC and disambiguate Burmese Zero (၀) vs Wa (ဝ).
    
    A Burmese digit Zero (၀, U+1040) immediately preceding or following a consonant,
    vowel, medial, asat, or virama is an optical or typing confusion for Burmese consonant Wa (ဝ, U+1015).
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    
    chars = list(text)
    n = len(chars)
    for idx in range(n):
        if chars[idx] == "၀":  # Burmese digit zero
            # Check next character: if followed by vowel/medial/asat/virama
            if idx + 1 < n:
                cp_next = ord(chars[idx + 1])
                if cp_next in _VOWELS_MEDIALS_SIGNS_ORD or cp_next in _CONSONANTS_ORD:
                    chars[idx] = "ဝ"
                    continue
            # Check previous character: if preceded by consonant (e.g. ဌ၀မ်း, သ၀န်)
            if idx > 0 and chars[idx] == "၀":
                cp_prev = ord(chars[idx - 1])
                if cp_prev in _CONSONANTS_ORD:
                    chars[idx] = "ဝ"
    return "".join(chars)
