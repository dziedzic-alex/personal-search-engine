import re
import unicodedata

# PyMuPDF sometimes returns font/CMap garbage instead of real text. These thresholds
# filter blocks that are not worth embedding
MIN_ALNUM = 3
MIN_PRINTABLE_RATIO = 0.85
MIN_PAGE_TEXT_LENGTH = 200


def is_printable_char(char: str) -> bool:
    if char in "\n\r\t ":
        return True

    # L/M/N/P/S/Z = letter, mark, number, punctuation, symbol, separator
    return unicodedata.category(char)[0] in "LMNPSZ"


def passes_text_quality_checks(text_block: str) -> bool:
    if not text_block or not text_block.strip():
        return False

    # Reject blocks that are mostly symbols or non-text bytes (e.g. "\x00\x45\x46...").
    printable_count = sum(1 for char in text_block if is_printable_char(char))
    if printable_count / len(text_block) < MIN_PRINTABLE_RATIO:
        return False

    # Need enough real content to be useful for search, not just punctuation.
    if sum(char.isalnum() for char in text_block) < MIN_ALNUM:
        return False

    # Require at least one word-like run so isolated noise does not get embedded.
    if not re.search(r"[\w]{2,}", text_block, re.UNICODE):
        return False

    return True


def is_text_block_usable(text_block: str) -> bool:
    if not text_block or not text_block.strip():
        return False

    # Binary junk often includes null bytes and other C0 control characters.
    if any(ord(char) < 32 and char not in "\n\r\t" for char in text_block):
        return False

    # A few undecodable glyphs may appear in otherwise good text; strip and re-check.
    without_replacement_chars = text_block.replace("\ufffd", "")

    return passes_text_quality_checks(without_replacement_chars)


def sanitize_text_block(text_block: str) -> str:
    # PDF blocks use newlines for layout; normalize to a single line for embedding.
    text = text_block.replace("\ufffd", "").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def should_fallback_to_image(text: str) -> bool:
    return len(text) < MIN_PAGE_TEXT_LENGTH
