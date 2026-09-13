"""wecos_ocr.linguistics: Syllable FSA, canonical normalizers, and orthographic repair."""

from .normalizer import clean_myanmar_canonical
from .orthography import MyanmarOrthographyGuard, get_myanmar_orthography_guard, repair_ocr_spelling
from .syllable import (
    Category,
    classify_char,
    is_valid_syllable,
    segment_syllables,
    syllable_break,
)

__all__ = [
    "Category",
    "classify_char",
    "clean_myanmar_canonical",
    "is_valid_syllable",
    "segment_syllables",
    "syllable_break",
    "MyanmarOrthographyGuard",
    "get_myanmar_orthography_guard",
    "repair_ocr_spelling",
]

