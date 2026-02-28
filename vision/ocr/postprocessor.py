"""OCR post-processor — regex validation and Tunisian plate normalization."""
from __future__ import annotations
import re


# Tunisian plate patterns:
#   New format:   123 TN 4567  (digits – TN/تونس – digits)
#   Old format:   12345  (pure digits for some categories)
_TUNISIAN_PLATE_RE = re.compile(r"^\d{1,4}\s*(?:TN|تونس)\s*\d{4}$", re.IGNORECASE)

# Arabic-to-Latin digit mapping
_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def normalize_raw_ocr(raw: str) -> str:
    """Normalize raw OCR output to a canonical plate string.

    - Convert Arabic digits → Latin digits
    - Normalize Arabic كلمة تونس → TN
    - Remove all whitespace / noise characters
    - Uppercase
    """
    text = raw.translate(_ARABIC_DIGITS)
    text = re.sub(r"تونس", "TN", text)
    text = re.sub(r"[^A-Z0-9]", "", text.upper())
    return text


def is_valid_plate(normalized: str) -> bool:
    """Return True if the normalized text looks like a Tunisian plate."""
    # After normalization: digits-TN-digits  e.g. "123TN4567"
    return bool(re.match(r"^\d{1,4}TN\d{4}$", normalized))


def post_process(raw: str, confidence: float) -> dict:
    """Full post-processing pipeline.

    Returns a dict with keys: plate, normalized, valid, confidence.
    """
    normalized = normalize_raw_ocr(raw)
    valid = is_valid_plate(normalized)
    return {
        "plate": raw,
        "normalized": normalized,
        "valid": valid,
        "confidence": round(confidence, 3),
    }
