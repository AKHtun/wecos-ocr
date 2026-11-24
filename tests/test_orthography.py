from wecos_ocr.linguistics.orthography import MyanmarOrthographyGuard

def test_optical_repairs():
    guard = MyanmarOrthographyGuard()
    raw = "ကကြီး- ခစွေး- ဂငယ်"
    repaired, telem = guard.repair_ocr_text(raw)
    assert "ခခွေး" in repaired
    assert telem["repairs"] >= 1

def test_ligature_and_noise_repair():
    guard = MyanmarOrthographyGuard()
    raw = "ဇက္ပဲ စျမျဉ်းဆွဲ ည\nတဝမ်းပူ ထဆင်ထူး ဒထွေး\nသမီးလေး လိမ်မာတယ်%"
    repaired, telem = guard.repair_ocr_text(raw)
    assert "ဇကွဲ" in repaired
    assert "ဈမျဉ်းဆွဲ" in repaired
    assert "ဒဒွေး" in repaired
    assert "လိမ်မာတယ်။" in repaired
    assert telem["lexical"] == 0  # dictionary guesser stays off unless asked

def test_dictionary_pass_is_opt_in():
    """Archaic Burmese must survive by default; the modern-dict guesser is opt-in only."""
    guard = MyanmarOrthographyGuard()
    raw = "ငွေသူရဘဏ် ခုနှစ်"

    default_out, telem = guard.repair_ocr_text(raw)
    assert default_out == raw
    assert telem["lexical"] == 0

    # document_year at/after MODERN_BURMESE_FROM opts in -- and demonstrably vandalises this text
    opted_out, _ = guard.repair_ocr_text(raw, document_year=2000)
    assert opted_out != raw
    assert "ခုနှစ်" not in opted_out

    # pre-modern year is still off
    premodern_out, pre_telem = guard.repair_ocr_text(raw, document_year=1889)
    assert premodern_out == raw
    assert pre_telem["lexical"] == 0

    # explicit override wins over the year
    assert guard.repair_ocr_text(raw, document_year=2000, use_dictionary=False)[1]["lexical"] == 0
