from tests.workers.document_processor.helpers import (
    added_embeddings,
    make_document,
    make_page,
    make_png_image_bytes,
)
from workers.document_processor.image.image import ImageIndexContext
from workers.document_processor.pdf.pdf import index_pdf


def test_text_rich_page_indexes_chunks_without_images(
    mock_pdf_session, mock_embedding_models, mocker
):
    page = make_page(text_blocks=["A" * 250])
    document = make_document([page])
    mock_index_image = mocker.patch("workers.document_processor.pdf.pdf.index_image")

    index_pdf(1, document)

    mock_index_image.assert_not_called()
    embeddings = added_embeddings(mock_pdf_session)
    assert len(embeddings) == 1
    assert embeddings[0].content == "A" * 250
    assert embeddings[0].text_embedding is not None


def test_scanned_page_uses_pixmap_fallback(
    mock_pdf_session, mock_embedding_models, mocker
):
    page = make_page(text_blocks=[])
    document = make_document([page])
    mock_index_image = mocker.patch(
        "workers.document_processor.pdf.pdf.index_image", return_value=True
    )

    index_pdf(1, document)

    mock_index_image.assert_called_once()
    assert mock_index_image.call_args.kwargs["context"] == ImageIndexContext.PDF_PAGE
    page.get_pixmap.assert_called_once()
    mock_embedding_models[0].encode.assert_not_called()
    mock_pdf_session.add.assert_not_called()


def test_embedded_image_uses_pdf_embedded_context(
    mock_pdf_session, mock_embedding_models, mocker
):
    page = make_page(text_blocks=[], images=[(5,)])
    document = make_document([page])
    document.extract_image.return_value = {"image": make_png_image_bytes()}
    mock_index_image = mocker.patch(
        "workers.document_processor.pdf.pdf.index_image", return_value=True
    )

    index_pdf(1, document)

    mock_index_image.assert_called_once()
    assert (
        mock_index_image.call_args.kwargs["context"] == ImageIndexContext.PDF_EMBEDDED
    )
    page.get_pixmap.assert_not_called()
    mock_embedding_models[0].encode.assert_not_called()


def test_pixmap_fallback_when_embedded_image_is_too_small(
    mock_pdf_session, mock_embedding_models, mocker
):
    page = make_page(text_blocks=[], images=[(5,)])
    document = make_document([page])
    document.extract_image.return_value = {"image": make_png_image_bytes()}
    mock_index_image = mocker.patch(
        "workers.document_processor.pdf.pdf.index_image", return_value=False
    )

    index_pdf(1, document)

    assert mock_index_image.call_count == 2
    assert (
        mock_index_image.call_args_list[0].kwargs["context"]
        == ImageIndexContext.PDF_EMBEDDED
    )
    assert (
        mock_index_image.call_args_list[1].kwargs["context"]
        == ImageIndexContext.PDF_PAGE
    )
    page.get_pixmap.assert_called_once()


def test_duplicate_xref_is_indexed_once(
    mock_pdf_session, mock_embedding_models, mocker
):
    rich_text = "C" * 250
    page_one = make_page(text_blocks=[rich_text], images=[(5,)], page_number=0)
    page_two = make_page(text_blocks=[rich_text], images=[(5,)], page_number=1)
    document = make_document([page_one, page_two])
    document.extract_image.return_value = {"image": make_png_image_bytes()}
    mock_index_image = mocker.patch(
        "workers.document_processor.pdf.pdf.index_image", return_value=True
    )

    index_pdf(1, document)

    mock_index_image.assert_called_once()
    assert (
        mock_index_image.call_args.kwargs["context"] == ImageIndexContext.PDF_EMBEDDED
    )
    document.extract_image.assert_called_once_with(5)
    page_one.get_pixmap.assert_not_called()
    page_two.get_pixmap.assert_not_called()


def test_extract_image_failure_falls_back_to_pixmap(
    mock_pdf_session, mock_embedding_models, mocker
):
    page = make_page(text_blocks=[], images=[(5,)])
    document = make_document([page])
    document.extract_image.side_effect = RuntimeError("bad xref")
    mock_index_image = mocker.patch(
        "workers.document_processor.pdf.pdf.index_image", return_value=True
    )

    index_pdf(1, document)

    mock_index_image.assert_called_once()
    assert mock_index_image.call_args.kwargs["context"] == ImageIndexContext.PDF_PAGE
    page.get_pixmap.assert_called_once()


def test_mixed_pdf_indexes_text_chunks_and_scanned_pages(
    mock_pdf_session, mock_embedding_models, mocker
):
    text_page = make_page(text_blocks=["B" * 250], page_number=0)
    scanned_page = make_page(text_blocks=[], page_number=1)
    document = make_document([text_page, scanned_page])
    mock_index_image = mocker.patch(
        "workers.document_processor.pdf.pdf.index_image", return_value=True
    )

    index_pdf(1, document)

    mock_index_image.assert_called_once()
    assert mock_index_image.call_args.kwargs["context"] == ImageIndexContext.PDF_PAGE
    embeddings = added_embeddings(mock_pdf_session)
    assert len(embeddings) == 1
    assert embeddings[0].content == "B" * 250
    scanned_page.get_pixmap.assert_called_once()
    text_page.get_pixmap.assert_not_called()
