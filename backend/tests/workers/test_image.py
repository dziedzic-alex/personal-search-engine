from tests.workers.helpers import added_embeddings, make_image
from workers.image import ImageIndexContext, index_image, should_encode_image_embedding
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


def test_index_image_skips_tiny_images(
    mock_image_session, mock_embedding_models, mocker
):
    mocker.patch("workers.image.pytesseract.image_to_string", return_value="caption")

    assert not index_image(1, make_image(width=32, height=32))

    mock_image_session.add.assert_not_called()


def test_photo_with_no_ocr_writes_image_embedding_only(
    mock_image_session, mock_embedding_models, mocker
):
    mocker.patch("workers.image.pytesseract.image_to_string", return_value="")

    assert index_image(1, make_image(), context=ImageIndexContext.PHOTO)

    embeddings = added_embeddings(mock_image_session)
    assert len(embeddings) == 1
    assert embeddings[0].image_embedding is not None
    assert embeddings[0].content is None


def test_photo_with_short_caption_writes_both_embeddings(
    mock_image_session, mock_embedding_models, mocker
):
    mocker.patch(
        "workers.image.pytesseract.image_to_string", return_value="Lake Tahoe 2024"
    )

    assert index_image(1, make_image(), context=ImageIndexContext.PHOTO)

    embeddings = added_embeddings(mock_image_session)
    assert len(embeddings) == 2
    assert any(
        embedding.content and embedding.text_embedding for embedding in embeddings
    )
    assert any(
        embedding.image_embedding and not embedding.content for embedding in embeddings
    )


def test_photo_with_long_ocr_writes_text_embedding_only(
    mock_image_session, mock_embedding_models, mocker
):
    long_text = "document " * 30
    mocker.patch("workers.image.pytesseract.image_to_string", return_value=long_text)

    assert index_image(1, make_image(), context=ImageIndexContext.PHOTO)

    embeddings = added_embeddings(mock_image_session)
    assert len(embeddings) == 1
    assert embeddings[0].content == long_text.strip()
    assert embeddings[0].text_embedding is not None
    assert embeddings[0].image_embedding is None


def test_photo_with_garbage_ocr_writes_image_embedding_only(
    mock_image_session, mock_embedding_models, mocker
):
    mocker.patch(
        "workers.image.pytesseract.image_to_string", return_value="|[] ]]] ||| ...."
    )

    assert index_image(1, make_image(), context=ImageIndexContext.PHOTO)

    embeddings = added_embeddings(mock_image_session)
    assert len(embeddings) == 1
    assert embeddings[0].image_embedding is not None
    assert embeddings[0].content is None


def test_pdf_page_with_good_ocr_writes_text_embedding_only(
    mock_image_session, mock_embedding_models, mocker
):
    text = "This quarterly earnings report summarizes regional revenue growth."
    mocker.patch("workers.image.pytesseract.image_to_string", return_value=text)

    assert index_image(1, make_image(), context=ImageIndexContext.PDF_PAGE)

    embeddings = added_embeddings(mock_image_session)
    assert len(embeddings) == 1
    assert embeddings[0].content == text
    assert embeddings[0].text_embedding is not None
    assert embeddings[0].image_embedding is None


def test_pdf_page_with_no_ocr_writes_image_embedding_only(
    mock_image_session, mock_embedding_models, mocker
):
    mocker.patch("workers.image.pytesseract.image_to_string", return_value="")

    assert index_image(1, make_image(), context=ImageIndexContext.PDF_PAGE)

    embeddings = added_embeddings(mock_image_session)
    assert len(embeddings) == 1
    assert embeddings[0].image_embedding is not None
    assert embeddings[0].content is None


def test_pdf_embedded_with_good_ocr_writes_text_embedding_only(
    mock_image_session, mock_embedding_models, mocker
):
    text = "Figure 2: Revenue increased across all regions in Q4."
    mocker.patch("workers.image.pytesseract.image_to_string", return_value=text)

    assert index_image(1, make_image(), context=ImageIndexContext.PDF_EMBEDDED)

    embeddings = added_embeddings(mock_image_session)
    assert len(embeddings) == 1
    assert embeddings[0].content == text
    assert embeddings[0].text_embedding is not None
    assert embeddings[0].image_embedding is None
