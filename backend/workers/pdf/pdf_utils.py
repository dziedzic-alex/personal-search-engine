from workers.text_quality import PDF_TEXT_BLOCK_PROFILE, passes_text_quality_checks

MIN_PAGE_TEXT_LENGTH = 200


def is_text_block_usable(text_block: str) -> bool:
    if not text_block or not text_block.strip():
        return False

    # Binary junk often includes null bytes and other C0 control characters.
    if any(ord(char) < 32 and char not in "\n\r\t" for char in text_block):
        return False

    # A few undecodable glyphs may appear in otherwise good text; strip and re-check.
    without_replacement_chars = text_block.replace("\ufffd", "")

    return passes_text_quality_checks(without_replacement_chars, PDF_TEXT_BLOCK_PROFILE)


def should_fallback_to_image(text: str) -> bool:
    return len(text) < MIN_PAGE_TEXT_LENGTH
