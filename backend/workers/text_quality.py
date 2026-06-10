import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class TextQualityProfile:
    min_length: int
    min_alnum: int
    min_printable_ratio: float


PDF_TEXT_BLOCK_PROFILE = TextQualityProfile(
    min_length=0, min_alnum=3, min_printable_ratio=0.85
)

OCR_PHOTO_PROFILE = TextQualityProfile(
    min_length=15, min_alnum=8, min_printable_ratio=0.8
)

OCR_PDF_PAGE_PROFILE = TextQualityProfile(
    min_length=30, min_alnum=15, min_printable_ratio=0.85
)

OCR_PDF_EMBEDDED_PROFILE = TextQualityProfile(
    min_length=20, min_alnum=10, min_printable_ratio=0.8
)


def is_printable_char(char: str) -> bool:
    if char in "\n\r\t ":
        return True

    # L/M/N/P/S/Z = letter, mark, number, punctuation, symbol, separator
    return unicodedata.category(char)[0] in "LMNPSZ"


def passes_text_quality_checks(text: str, profile: TextQualityProfile) -> bool:
    if not text or not text.strip():
        return False

    if len(text) < profile.min_length:
        return False

    printable_count = sum(1 for char in text if is_printable_char(char))
    if printable_count / len(text) < profile.min_printable_ratio:
        return False

    if sum(char.isalnum() for char in text) < profile.min_alnum:
        return False

    if not re.search(r"[\w]{2,}", text, re.UNICODE):
        return False

    return True


def sanitize_text(text: str) -> str:
    text = text.replace("\ufffd", "")
    return re.sub(r"\s+", " ", text).strip()
