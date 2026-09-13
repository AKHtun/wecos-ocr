from PIL import Image
from wecos_ocr.vision.enhancer import enhance_scanned_plate, is_yellowed_or_low_contrast

def test_vision_enhancer():
    # Synthetic yellowed scan image
    yellow_img = Image.new("RGB", (100, 100), color=(240, 230, 180))
    assert is_yellowed_or_low_contrast(yellow_img) is True
    enhanced = enhance_scanned_plate(yellow_img)
    assert enhanced.size == (100, 100)

def test_clean_white_image():
    # Clean white background image should not be flagged as heavily yellowed
    white_img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    assert is_yellowed_or_low_contrast(white_img) is False
