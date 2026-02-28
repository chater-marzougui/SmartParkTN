"""Plate normalization utilities shared across backend and vision."""
import re
import unicodedata


def normalize_plate(raw: str) -> str:
    """
    Normalize a Tunisian plate number for consistent DB storage.
    Handles Arabic 'تونس' and digit variations.
    Returns uppercase alphanumeric string, e.g. '123TN5678'.
    """
    if not raw:
        return ""
    # Remove whitespace
    text = raw.strip()
    # Replace Arabic word تونس with TN
    text = text.replace("تونس", "TN").replace("TUNISIE", "TN")
    # Remove remaining Arabic characters
    text = re.sub(r"[\u0600-\u06FF]", "", text)
    # Keep digits, uppercase letters, spaces
    text = re.sub(r"[^A-Za-z0-9\s]", "", text)
    text = text.upper().replace(" ", "")
    return text


def validate_plate(normalized: str) -> bool:
    """Check if a normalized plate matches known Tunisian formats."""
    patterns = [
        r"^\d{1,4}TN\d{1,4}$",    # standard: 123TN5678
        r"^\d{1,4}RS\d{1,4}$",    # government
        r"^\d{1,7}$",             # old format (digits only)
    ]
    return any(re.match(p, normalized) for p in patterns)
