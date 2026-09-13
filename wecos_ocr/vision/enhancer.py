"""Adaptive Scanned-Plate Vision Preprocessor.

Specialized for:
- Aged, yellowed, and stained letterpress paper.
- Low-contrast historical monographs and lithic rubbings.
- Background normalization and ink darkening for VLM OCR.
"""

from typing import Union
from PIL import Image, ImageEnhance, ImageOps
import numpy as np


def is_yellowed_or_low_contrast(image: Image.Image) -> bool:
    """Detect whether a scanned document plate is yellowed, aged, or low contrast."""
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Downsample for fast heuristic check
    small = image.resize((64, 64), Image.Resampling.BILINEAR)
    arr = np.array(small, dtype=np.float32)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    mean_r = np.mean(r)
    mean_g = np.mean(g)
    mean_b = np.mean(b)

    # Yellowing heuristic: Red and Green significantly higher than Blue
    yellow_delta = (mean_r + mean_g) / 2.0 - mean_b
    is_yellowed = bool(yellow_delta > 20.0 and mean_r > 160.0)

    # Low contrast heuristic: standard deviation of luminance (excluding pure blank white)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    mean_lum = np.mean(lum)
    std_lum = np.std(lum)
    is_low_contrast = bool(std_lum < 35.0 and mean_lum < 240.0)

    return is_yellowed or is_low_contrast



def enhance_scanned_plate(
    image: Image.Image,
    contrast_factor: float = 1.4,
    autocontrast_cutoff: int = 2,
    to_grayscale: bool = False,
) -> Image.Image:
    """Enhance document scan by stretching contrast, whitening aged background, and sharpening ink."""
    if image.mode != "RGB":
        image = image.convert("RGB")

    # 1. Stretch dynamic range (whitens dirty background, deepens ink)
    enhanced = ImageOps.autocontrast(image, cutoff=autocontrast_cutoff)

    # 2. Boost local text contrast
    if contrast_factor != 1.0:
        enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = enhancer.enhance(contrast_factor)

    # 3. Optional grayscale normalization
    if to_grayscale:
        enhanced = enhanced.convert("L").convert("RGB")

    return enhanced
