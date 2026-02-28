"""Image preprocessor for license plate OCR."""
from __future__ import annotations
import cv2
import numpy as np


def preprocess_plate(image: np.ndarray) -> np.ndarray:
    """Apply a robust preprocessing pipeline for OCR accuracy.

    Steps: grayscale → CLAHE → deskew → resize → denoise
    """
    # 1. Grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # 2. CLAHE for contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    enhanced = clahe.apply(gray)

    # 3. Resize to a standard width (300 px) keeping aspect ratio
    h, w = enhanced.shape
    target_w = 300
    target_h = max(1, int(h * target_w / w))
    resized = cv2.resize(enhanced, (target_w, target_h), interpolation=cv2.INTER_CUBIC)

    # 4. Deskew via Hough lines
    resized = _deskew(resized)

    # 5. Light denoising
    denoised = cv2.fastNlMeansDenoising(resized, h=10)

    return denoised


def _deskew(image: np.ndarray) -> np.ndarray:
    """Detect dominant angle via Hough lines and rotate to correct skew."""
    edges = cv2.Canny(image, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=30, maxLineGap=10)
    if lines is None:
        return image
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 != x1:
            angles.append(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
    if not angles:
        return image
    median_angle = float(np.median(angles))
    if abs(median_angle) < 1:
        return image
    h, w = image.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), median_angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
