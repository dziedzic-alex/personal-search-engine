from workers.image import ImageIndexContext, should_encode_image_embedding
from workers.text_quality import OCR_PDF_PAGE_PROFILE, passes_text_quality_checks


def test_photo_includes_image_embedding_when_ocr_is_empty():
    assert should_encode_image_embedding(
        ImageIndexContext.PHOTO, "", has_text_embedding=False
    )


def test_photo_includes_both_embeddings_for_short_caption():
    assert should_encode_image_embedding(
        ImageIndexContext.PHOTO, "Lake Tahoe 2024", has_text_embedding=True
    )


def test_photo_skips_image_embedding_for_long_document_like_ocr():
    long_text = "a" * 200
    assert not should_encode_image_embedding(
        ImageIndexContext.PHOTO, long_text, has_text_embedding=True
    )


def test_pdf_page_skips_image_embedding_when_ocr_succeeds():
    text = "This quarterly earnings report summarizes regional revenue growth."
    assert passes_text_quality_checks(text, OCR_PDF_PAGE_PROFILE)
    assert not should_encode_image_embedding(
        ImageIndexContext.PDF_PAGE, text, has_text_embedding=True
    )


def test_pdf_page_includes_image_embedding_when_ocr_fails():
    assert should_encode_image_embedding(
        ImageIndexContext.PDF_PAGE, "", has_text_embedding=False
    )
