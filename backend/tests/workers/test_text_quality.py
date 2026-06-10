from workers.text_quality import (
    OCR_PDF_PAGE_PROFILE,
    OCR_PHOTO_PROFILE,
    PDF_TEXT_BLOCK_PROFILE,
    passes_text_quality_checks,
    sanitize_text,
)


def test_passes_text_quality_checks_accepts_normal_text():
    assert passes_text_quality_checks("Hello world from a PDF page", PDF_TEXT_BLOCK_PROFILE)


def test_passes_text_quality_checks_rejects_too_few_alphanumeric_characters():
    assert not passes_text_quality_checks("!!", OCR_PHOTO_PROFILE)


def test_photo_profile_accepts_short_caption():
    assert passes_text_quality_checks("Lake Tahoe 2024", OCR_PHOTO_PROFILE)


def test_photo_profile_rejects_ocr_garbage():
    assert not passes_text_quality_checks("|[] ]]] ||| ....", OCR_PHOTO_PROFILE)


def test_pdf_page_profile_requires_more_text_than_photo():
    text = "Short receipt scan"
    assert passes_text_quality_checks(text, OCR_PHOTO_PROFILE)
    assert not passes_text_quality_checks(text, OCR_PDF_PAGE_PROFILE)


def test_sanitize_text_collapses_whitespace_and_strips_replacement_characters():
    assert sanitize_text("Hello\ufffd\n\n  world") == "Hello world"
