from datetime import datetime

from sqlalchemy.dialects import postgresql

from workers.document_processor.pdf.pdf_utils import (
    extract_pdf_metadata,
    is_text_block_usable,
    merge_text_blocks_into_chunks,
    should_fallback_to_image,
)


def _source_created_time_from_execute(mock_session) -> datetime:
    statement = mock_session.execute.call_args[0][0]
    params = statement.compile(dialect=postgresql.dialect()).params
    return params["source_created_time"]


def test_is_text_block_usable_accepts_normal_text():
    assert is_text_block_usable("Hello world from a PDF page")


def test_is_text_block_usable_rejects_null_bytes():
    assert not is_text_block_usable("Hello\x00world")


def test_is_text_block_usable_rejects_control_characters():
    assert not is_text_block_usable("Hello\x01world")


def test_is_text_block_usable_accepts_text_with_few_replacement_characters():
    assert is_text_block_usable("Hello\ufffd world from a PDF page")


def test_is_text_block_usable_rejects_when_stripping_replacement_chars_leaves_unusable_text():
    assert not is_text_block_usable("\ufffd\ufffd!!")


def test_is_text_block_usable_rejects_mostly_non_printable_garbage():
    assert not is_text_block_usable("\x00\x45\x46\x47\x48")


def test_is_text_block_usable_rejects_whitespace_only():
    assert not is_text_block_usable("   \n\t  ")


def test_is_text_block_usable_rejects_too_few_alphanumeric_characters():
    assert not is_text_block_usable("!!")


def test_merge_text_blocks_combines_small_blocks_into_one_chunk():
    blocks = ["Amount", "Federal tax", "Wages"] + ["extra word"] * 30
    chunks = merge_text_blocks_into_chunks(blocks)

    assert len(chunks) == 1
    assert "Amount" in chunks[0]
    assert "Federal tax" in chunks[0]
    assert len(chunks[0]) >= 300


def test_merge_text_blocks_skips_empty_and_whitespace_only_blocks():
    blocks = ["", "   ", "\n\t", "Amount", "Federal tax"] + ["extra word"] * 30
    chunks = merge_text_blocks_into_chunks(blocks)

    assert len(chunks) == 1
    assert chunks[0].startswith("Amount")
    assert "Federal tax" in chunks[0]
    assert len(chunks[0]) >= 300


def test_merge_text_blocks_appends_short_remainder_to_previous_chunk():
    blocks = ["A" * 320, "tail"]
    chunks = merge_text_blocks_into_chunks(blocks)

    assert len(chunks) == 1
    assert chunks[0].endswith("tail")


def test_merge_text_blocks_appends_tail_as_single_chunk():
    blocks = ["A" * 250]
    chunks = merge_text_blocks_into_chunks(blocks)

    assert len(chunks) == 1
    assert len(chunks[0]) == 250


def test_merge_text_blocks_splits_oversized_text():
    blocks = ["A" * 1600]
    chunks = merge_text_blocks_into_chunks(blocks)

    assert len(chunks) >= 2
    assert all(len(chunk) <= 1500 for chunk in chunks)


def test_should_fallback_to_image_when_page_text_is_short():
    assert should_fallback_to_image("short page text")


def test_should_not_fallback_to_image_when_page_text_is_long_enough():
    assert not should_fallback_to_image("A" * 200)


def test_extract_pdf_metadata_uses_creation_date(mocker, mock_pdf_utils_session):
    document = mocker.MagicMock()
    document.metadata = {
        "creationDate": "D:20260412172229Z",
        "modDate": "",
    }

    extract_pdf_metadata(document, document_id=1)

    mock_pdf_utils_session.execute.assert_called_once()
    mock_pdf_utils_session.commit.assert_called_once()
    assert _source_created_time_from_execute(mock_pdf_utils_session) == datetime(
        2026, 4, 12, 17, 22, 29
    )


def test_extract_pdf_metadata_falls_back_to_mod_date(mocker, mock_pdf_utils_session):
    document = mocker.MagicMock()
    document.metadata = {
        "creationDate": "",
        "modDate": "D:20260501120219-04'00'",
    }

    extract_pdf_metadata(document, document_id=2)

    mock_pdf_utils_session.execute.assert_called_once()
    assert _source_created_time_from_execute(mock_pdf_utils_session) == datetime(
        2026, 5, 1, 16, 2, 19
    )


def test_extract_pdf_metadata_skips_when_no_dates(mocker, mock_pdf_utils_session):
    document = mocker.MagicMock()
    document.metadata = {"creationDate": "", "modDate": ""}

    extract_pdf_metadata(document, document_id=3)

    mock_pdf_utils_session.execute.assert_not_called()
    mock_pdf_utils_session.commit.assert_not_called()


def test_extract_pdf_metadata_skips_on_invalid_creation_date(
    mocker, mock_pdf_utils_session
):
    document = mocker.MagicMock()
    document.metadata = {
        "creationDate": "not-a-pdf-date",
        "modDate": "not-a-pdf-date",
    }

    extract_pdf_metadata(document, document_id=4)

    mock_pdf_utils_session.execute.assert_not_called()
