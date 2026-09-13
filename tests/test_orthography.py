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
