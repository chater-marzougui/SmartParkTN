"""EasyOCR engine wrapper for bilingual (Arabic + Latin) Tunisian plates."""
from __future__ import annotations
from typing import Tuple
import numpy as np
import easyocr

from vision.ocr.preprocessor import preprocess_plate

# Singleton reader — instantiation is expensive
_reader: easyocr.Reader | None = None


def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        # Arabic + English covers Tunisian plates (Arabic numerals + تونس)
        _reader = easyocr.Reader(["ar", "en"], gpu=False)
    return _reader


def read_plate(crop: np.ndarray) -> Tuple[str, float]:
    """Run OCR on a cropped plate image.

    Returns (raw_text, confidence) where confidence is 0-1.
    """
    processed = preprocess_plate(crop)
    reader = _get_reader()
    results = reader.readtext(processed, detail=1, paragraph=False)
    if not results:
        return "", 0.0

    # Concatenate all detected text regions, sorted left-to-right
    results_sorted = sorted(results, key=lambda r: r[0][0][0])  # sort by x1 of bbox
    raw_text = " ".join(r[1] for r in results_sorted).strip()
    avg_conf = float(np.mean([r[2] for r in results_sorted]))
    return raw_text, avg_conf
