from PIL import Image
import wecos_ocr

def test_transcribe_facade(monkeypatch):
    test_img = Image.new("RGB", (50, 50), color=(255, 255, 255))
    # Mock backend to return test raw OCR string with optical confusion
    monkeypatch.setattr(
        "wecos_ocr.backends.ollama.OllamaBackend.ocr_image",
        lambda self, img, prompt="": "ကကြီး- ခစွေး- ဂငယ်"
    )
    
    res = wecos_ocr.transcribe(test_img, backend="ollama", enhance=False, repair=True)
    assert res.text == "ကကြီး- ခခွေး- ဂငယ်"
    assert res.engine == "ollama"
    assert res.telemetry["repairs"] >= 1
