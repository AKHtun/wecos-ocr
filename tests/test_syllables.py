from wecos_ocr.linguistics import segment_syllables, syllable_break, clean_myanmar_canonical

def test_zin_maung_maung_table_7():
    assert segment_syllables("အဗ္ဘန္တရသရက်") == ["အဗ္ဘန္တ", "ရ", "သ", "ရက်"]
    assert segment_syllables("ဥတ္တရယဉ်စွန်းတန်း") == ["ဥတ္တ", "ရ", "ယဉ်", "စွန်း", "တန်း"]
    assert segment_syllables("မင်္ဂလာ") == ["မင်္ဂ", "လာ"]
    assert segment_syllables("ယောက်ျား") == ["ယောက်ျား"]
    assert segment_syllables("မားစ်ဂိုဟ်") == ["မားစ်", "ဂိုဟ်"]
    assert segment_syllables("မနုဿီဟ") == ["မ", "နုဿီ", "ဟ"]
    assert segment_syllables("ကက်ရှ်မီးယား") == ["ကက်ရှ်", "မီး", "ယား"]

def test_zero_wa_disambiguation():
    assert clean_myanmar_canonical("ဌ၀မ်းဘဲ") == "ဌဝမ်းဘဲ"
    assert clean_myanmar_canonical("သ၀န်") == "သဝန်"
