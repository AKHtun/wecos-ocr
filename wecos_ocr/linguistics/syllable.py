"""Sovereign Myanmar Syllable Segmentation Engine.

Formalized from:
    "A Rule-based Syllable Segmentation of Myanmar Text"
    Zin Maung Maung & Yoshiki Mikami (IJCNLP-08, Hyderabad, India, 2008).
"""

from enum import IntEnum
from functools import lru_cache
from typing import List, Tuple

from .normalizer import clean_myanmar_canonical


class Category(IntEnum):
    C = 0   # Consonants
    M = 1   # Medials
    V = 2   # Dependent Vowels
    S = 3   # Sign Virama (U+1039)
    A = 4   # Sign Asat (U+103A)
    F = 5   # Dependent Various Signs (ံ, ့, း)
    I = 6   # Standalone Independent Vowels (ဤ, ဧ, ဪ, ၌, ၍, ၏)
    E = 7   # Combinable Independent Vowels (ဣ, ဥ, ဦ, ဩ, ၎)
    G = 8   # Great Sa (ဿ, U+103F)
    D = 9   # Digits (၀..၉)
    P = 10  # Punctuation (၊, ။)
    W = 11  # Whitespace
    O = 12  # Other / Foreign characters


_CONSONANTS = set("ကခဂဃငစဆဇဈဉညဋဌဍဎဏတထဒဓနပဖဗဘမယရလဝသဟဠအၐၑၒၓၔၕၛ")
_MEDIALS = set("ျြွှၖၗၘၙ")
_VOWELS = set("ါာိီုူေဲဳဴဵ")
_VIRAMA = {"\u1039"}
_ASAT = {"\u103A"}
_SIGNS_F = {"\u1036", "\u1037", "\u1038"}
_INDEP_I = {"\u1024", "\u1027", "\u102A", "\u104C", "\u104D", "\u104F"}
_INDEP_E = {"\u1023", "\u1025", "\u1026", "\u1029", "\u104E"}
_GREAT_SA = {"\u103F"}
_DIGITS = set("၀၁၂၃၄၅၆၇၈၉")
_PUNCTUATION = {"\u104A", "\u104B"}
_WHITESPACE = {" ", "\t", "\n", "\r", "\u00A0", "\u200B", "\u200C", "\u200D"}

_U = 99


def classify_char(char: str) -> Category:
    if char in _CONSONANTS:
        return Category.C
    if char in _MEDIALS:
        return Category.M
    if char in _VOWELS:
        return Category.V
    if char in _VIRAMA:
        return Category.S
    if char in _ASAT:
        return Category.A
    if char in _SIGNS_F:
        return Category.F
    if char in _INDEP_I:
        return Category.I
    if char in _INDEP_E:
        return Category.E
    if char in _GREAT_SA:
        return Category.G
    if char in _DIGITS:
        return Category.D
    if char in _PUNCTUATION:
        return Category.P
    if char in _WHITESPACE:
        return Category.W
    return Category.O


TABLE_4: dict[Tuple[Category, Category], int] = {
    # 1st = A
    (Category.A, Category.A): -1,
    (Category.A, Category.C): _U,
    (Category.A, Category.D): 1,
    (Category.A, Category.E): 1,
    (Category.A, Category.F): 0,
    (Category.A, Category.G): -1,
    (Category.A, Category.I): 1,
    (Category.A, Category.M): 0,
    (Category.A, Category.P): 1,
    (Category.A, Category.S): 0,
    (Category.A, Category.V): 0,
    (Category.A, Category.W): 1,

    # 1st = C
    (Category.C, Category.A): 0,
    (Category.C, Category.C): _U,
    (Category.C, Category.D): 1,
    (Category.C, Category.E): 1,
    (Category.C, Category.F): 0,
    (Category.C, Category.G): 0,
    (Category.C, Category.I): 1,
    (Category.C, Category.M): 0,
    (Category.C, Category.P): 1,
    (Category.C, Category.S): 0,
    (Category.C, Category.V): 0,
    (Category.C, Category.W): 1,

    # 1st = D
    (Category.D, Category.A): -1,
    (Category.D, Category.C): 1,
    (Category.D, Category.D): 0,
    (Category.D, Category.E): 1,
    (Category.D, Category.F): -1,
    (Category.D, Category.G): -1,
    (Category.D, Category.I): 1,
    (Category.D, Category.M): -1,
    (Category.D, Category.P): 1,
    (Category.D, Category.S): -1,
    (Category.D, Category.V): -1,
    (Category.D, Category.W): 1,

    # 1st = E
    (Category.E, Category.A): 0,
    (Category.E, Category.C): _U,
    (Category.E, Category.D): 1,
    (Category.E, Category.E): 1,
    (Category.E, Category.F): 0,
    (Category.E, Category.G): 0,
    (Category.E, Category.I): 1,
    (Category.E, Category.M): -1,
    (Category.E, Category.P): 1,
    (Category.E, Category.S): 0,
    (Category.E, Category.V): 0,
    (Category.E, Category.W): 1,

    # 1st = F
    (Category.F, Category.A): -1,
    (Category.F, Category.C): _U,
    (Category.F, Category.D): 1,
    (Category.F, Category.E): 1,
    (Category.F, Category.F): 0,
    (Category.F, Category.G): -1,
    (Category.F, Category.I): 1,
    (Category.F, Category.M): -1,
    (Category.F, Category.P): 1,
    (Category.F, Category.S): -1,
    (Category.F, Category.V): -1,
    (Category.F, Category.W): 1,

    # 1st = G
    (Category.G, Category.A): -1,
    (Category.G, Category.C): 1,
    (Category.G, Category.D): 1,
    (Category.G, Category.E): 1,
    (Category.G, Category.F): 0,
    (Category.G, Category.G): -1,
    (Category.G, Category.I): 1,
    (Category.G, Category.M): -1,
    (Category.G, Category.P): 1,
    (Category.G, Category.S): -1,
    (Category.G, Category.V): 0,
    (Category.G, Category.W): 1,

    # 1st = I
    (Category.I, Category.A): -1,
    (Category.I, Category.C): 1,
    (Category.I, Category.D): 1,
    (Category.I, Category.E): 1,
    (Category.I, Category.F): -1,
    (Category.I, Category.G): -1,
    (Category.I, Category.I): 1,
    (Category.I, Category.M): -1,
    (Category.I, Category.P): 1,
    (Category.I, Category.S): -1,
    (Category.I, Category.V): -1,
    (Category.I, Category.W): 1,

    # 1st = M
    (Category.M, Category.A): 2,
    (Category.M, Category.C): _U,
    (Category.M, Category.D): 1,
    (Category.M, Category.E): 1,
    (Category.M, Category.F): 0,
    (Category.M, Category.G): 0,
    (Category.M, Category.I): 1,
    (Category.M, Category.M): 0,
    (Category.M, Category.P): 1,
    (Category.M, Category.S): -1,
    (Category.M, Category.V): 0,
    (Category.M, Category.W): 1,

    # 1st = P
    (Category.P, Category.A): -1,
    (Category.P, Category.C): 1,
    (Category.P, Category.D): 1,
    (Category.P, Category.E): 1,
    (Category.P, Category.F): -1,
    (Category.P, Category.G): -1,
    (Category.P, Category.I): 1,
    (Category.P, Category.M): -1,
    (Category.P, Category.P): 0,
    (Category.P, Category.S): -1,
    (Category.P, Category.V): -1,
    (Category.P, Category.W): 1,

    # 1st = S
    (Category.S, Category.A): -1,
    (Category.S, Category.C): 0,
    (Category.S, Category.D): -1,
    (Category.S, Category.E): -1,
    (Category.S, Category.F): -1,
    (Category.S, Category.G): -1,
    (Category.S, Category.I): -1,
    (Category.S, Category.M): -1,
    (Category.S, Category.P): -1,
    (Category.S, Category.S): -1,
    (Category.S, Category.V): -1,
    (Category.S, Category.W): -1,

    # 1st = V
    (Category.V, Category.A): 2,
    (Category.V, Category.C): _U,
    (Category.V, Category.D): 1,
    (Category.V, Category.E): 1,
    (Category.V, Category.F): 0,
    (Category.V, Category.G): 0,
    (Category.V, Category.I): 1,
    (Category.V, Category.M): -1,
    (Category.V, Category.P): 1,
    (Category.V, Category.S): -1,
    (Category.V, Category.V): 0,
    (Category.V, Category.W): 1,

    # 1st = W
    (Category.W, Category.A): -1,
    (Category.W, Category.C): 1,
    (Category.W, Category.D): 1,
    (Category.W, Category.E): 1,
    (Category.W, Category.F): -1,
    (Category.W, Category.G): -1,
    (Category.W, Category.I): 1,
    (Category.W, Category.M): -1,
    (Category.W, Category.P): 1,
    (Category.W, Category.S): -1,
    (Category.W, Category.V): -1,
    (Category.W, Category.W): 0,
}

TABLE_5: dict[Tuple[Tuple[Category, Category], Category], int] = {
    # AC + 3rd
    ((Category.A, Category.C), Category.A): 3,
    ((Category.A, Category.C), Category.C): 1,
    ((Category.A, Category.C), Category.D): 1,
    ((Category.A, Category.C), Category.E): 1,
    ((Category.A, Category.C), Category.F): 1,
    ((Category.A, Category.C), Category.G): 1,
    ((Category.A, Category.C), Category.I): 1,
    ((Category.A, Category.C), Category.M): _U,
    ((Category.A, Category.C), Category.P): 1,
    ((Category.A, Category.C), Category.S): 1,
    ((Category.A, Category.C), Category.V): 1,
    ((Category.A, Category.C), Category.W): 1,

    # CC + 3rd
    ((Category.C, Category.C), Category.A): 0,
    ((Category.C, Category.C), Category.C): 1,
    ((Category.C, Category.C), Category.D): 1,
    ((Category.C, Category.C), Category.E): 1,
    ((Category.C, Category.C), Category.F): 1,
    ((Category.C, Category.C), Category.G): 1,
    ((Category.C, Category.C), Category.I): 1,
    ((Category.C, Category.C), Category.M): 1,
    ((Category.C, Category.C), Category.P): 1,
    ((Category.C, Category.C), Category.S): 0,
    ((Category.C, Category.C), Category.V): 1,
    ((Category.C, Category.C), Category.W): 1,

    # EC + 3rd
    ((Category.E, Category.C), Category.A): 0,
    ((Category.E, Category.C), Category.C): 1,
    ((Category.E, Category.C), Category.D): 1,
    ((Category.E, Category.C), Category.E): 1,
    ((Category.E, Category.C), Category.F): 1,
    ((Category.E, Category.C), Category.G): 1,
    ((Category.E, Category.C), Category.I): 1,
    ((Category.E, Category.C), Category.M): 1,
    ((Category.E, Category.C), Category.P): 1,
    ((Category.E, Category.C), Category.S): 0,
    ((Category.E, Category.C), Category.V): 1,
    ((Category.E, Category.C), Category.W): 1,

    # FC + 3rd
    ((Category.F, Category.C), Category.A): 3,
    ((Category.F, Category.C), Category.C): 1,
    ((Category.F, Category.C), Category.D): 1,
    ((Category.F, Category.C), Category.E): 1,
    ((Category.F, Category.C), Category.F): 1,
    ((Category.F, Category.C), Category.G): 1,
    ((Category.F, Category.C), Category.I): 1,
    ((Category.F, Category.C), Category.M): _U,
    ((Category.F, Category.C), Category.P): 1,
    ((Category.F, Category.C), Category.S): 1,
    ((Category.F, Category.C), Category.V): 1,
    ((Category.F, Category.C), Category.W): 1,

    # MC + 3rd
    ((Category.M, Category.C), Category.A): 0,
    ((Category.M, Category.C), Category.C): 1,
    ((Category.M, Category.C), Category.D): 1,
    ((Category.M, Category.C), Category.E): 1,
    ((Category.M, Category.C), Category.F): 1,
    ((Category.M, Category.C), Category.G): 1,
    ((Category.M, Category.C), Category.I): 1,
    ((Category.M, Category.C), Category.M): 1,
    ((Category.M, Category.C), Category.P): 1,
    ((Category.M, Category.C), Category.S): 0,
    ((Category.M, Category.C), Category.V): 1,
    ((Category.M, Category.C), Category.W): 1,

    # VC + 3rd
    ((Category.V, Category.C), Category.A): 0,
    ((Category.V, Category.C), Category.C): 1,
    ((Category.V, Category.C), Category.D): 1,
    ((Category.V, Category.C), Category.E): 1,
    ((Category.V, Category.C), Category.F): 1,
    ((Category.V, Category.C), Category.G): 1,
    ((Category.V, Category.C), Category.I): 1,
    ((Category.V, Category.C), Category.M): _U,
    ((Category.V, Category.C), Category.P): 1,
    ((Category.V, Category.C), Category.S): 0,
    ((Category.V, Category.C), Category.V): 1,
    ((Category.V, Category.C), Category.W): 1,
}

TABLE_6: dict[Tuple[Tuple[Category, Category, Category], Category], int] = {
    # ACM + 4th
    ((Category.A, Category.C, Category.M), Category.A): 4,
    ((Category.A, Category.C, Category.M), Category.C): 1,
    ((Category.A, Category.C, Category.M), Category.D): 1,
    ((Category.A, Category.C, Category.M), Category.E): 1,
    ((Category.A, Category.C, Category.M), Category.F): 1,
    ((Category.A, Category.C, Category.M), Category.G): 1,
    ((Category.A, Category.C, Category.M), Category.I): 1,
    ((Category.A, Category.C, Category.M), Category.M): 1,
    ((Category.A, Category.C, Category.M), Category.P): 1,
    ((Category.A, Category.C, Category.M), Category.S): 1,
    ((Category.A, Category.C, Category.M), Category.V): 1,
    ((Category.A, Category.C, Category.M), Category.W): 1,

    # FCM + 4th
    ((Category.F, Category.C, Category.M), Category.A): 4,
    ((Category.F, Category.C, Category.M), Category.C): 1,
    ((Category.F, Category.C, Category.M), Category.D): 1,
    ((Category.F, Category.C, Category.M), Category.E): 1,
    ((Category.F, Category.C, Category.M), Category.F): 1,
    ((Category.F, Category.C, Category.M), Category.G): 1,
    ((Category.F, Category.C, Category.M), Category.I): 1,
    ((Category.F, Category.C, Category.M), Category.M): 1,
    ((Category.F, Category.C, Category.M), Category.P): 1,
    ((Category.F, Category.C, Category.M), Category.S): 1,
    ((Category.F, Category.C, Category.M), Category.V): 1,
    ((Category.F, Category.C, Category.M), Category.W): 1,

    # VCM + 4th
    ((Category.V, Category.C, Category.M), Category.A): 4,
    ((Category.V, Category.C, Category.M), Category.C): 1,
    ((Category.V, Category.C, Category.M), Category.D): 1,
    ((Category.V, Category.C, Category.M), Category.E): 1,
    ((Category.V, Category.C, Category.M), Category.F): 1,
    ((Category.V, Category.C, Category.M), Category.G): 1,
    ((Category.V, Category.C, Category.M), Category.I): 1,
    ((Category.V, Category.C, Category.M), Category.M): 1,
    ((Category.V, Category.C, Category.M), Category.P): 1,
    ((Category.V, Category.C, Category.M), Category.S): 1,
    ((Category.V, Category.C, Category.M), Category.V): 1,
    ((Category.V, Category.C, Category.M), Category.W): 1,
}


@lru_cache(maxsize=4096)
def segment_syllables(text: str) -> List[str]:
    """Segment a continuous Myanmar text string into phonological syllable units."""
    if not text:
        return []

    text = clean_myanmar_canonical(text)
    chars = list(text)
    cats = [classify_char(c) for c in chars]
    n = len(chars)

    syllables: List[str] = []
    current_buf: List[str] = []
    i = 0

    while i < n:
        if i == n - 1:
            current_buf.append(chars[i])
            syllables.append("".join(current_buf))
            current_buf = []
            break

        c1 = cats[i]
        c2 = cats[i + 1]

        if c1 == Category.O or c2 == Category.O:
            current_buf.append(chars[i])
            if c1 != c2:
                syllables.append("".join(current_buf))
                current_buf = []
            i += 1
            continue

        status = TABLE_4.get((c1, c2), 1)

        if status == _U:
            if i + 2 < n:
                c3 = cats[i + 2]
                status = TABLE_5.get(((c1, c2), c3), 1)
            else:
                status = 1

        if status == _U:
            if i + 3 < n:
                c3 = cats[i + 2]
                c4 = cats[i + 3]
                status = TABLE_6.get(((c1, c2, c3), c4), 1)
            else:
                status = 1

        if status == 0:
            current_buf.append(chars[i])
            i += 1
        elif status == 1:
            current_buf.append(chars[i])
            syllables.append("".join(current_buf))
            current_buf = []
            i += 1
        elif status == 2:
            current_buf.append(chars[i])
            current_buf.append(chars[i + 1])
            syllables.append("".join(current_buf))
            current_buf = []
            i += 2
        elif status == 3:
            current_buf.append(chars[i])
            current_buf.append(chars[i + 1])
            current_buf.append(chars[i + 2])
            syllables.append("".join(current_buf))
            current_buf = []
            i += 3
        elif status == 4:
            current_buf.append(chars[i])
            current_buf.append(chars[i + 1])
            current_buf.append(chars[i + 2])
            current_buf.append(chars[i + 3])
            syllables.append("".join(current_buf))
            current_buf = []
            i += 4
        else:
            current_buf.append(chars[i])
            i += 1

    if current_buf:
        syllables.append("".join(current_buf))

    return syllables


def syllable_break(text: str, delimiter: str = "|") -> str:
    """Convenience function: insert delimiter at every syllable boundary."""
    sylls = segment_syllables(text)
    return delimiter + delimiter.join(sylls) + delimiter if sylls else ""


def is_valid_syllable(syl: str) -> bool:
    """Verify whether a segmented token conforms to canonical Myanmar phonotactic BNF."""
    if not syl:
        return False
    if all(classify_char(c) in (Category.W, Category.P, Category.D, Category.I) for c in syl):
        return True
    
    cats = [classify_char(c) for c in syl]
    if cats[0] not in (Category.C, Category.E, Category.I, Category.D, Category.P, Category.W, Category.O):
        return False
    
    for idx, cat in enumerate(cats):
        if cat == Category.S:
            if idx + 1 >= len(cats) or cats[idx + 1] != Category.C:
                return False
    return True
