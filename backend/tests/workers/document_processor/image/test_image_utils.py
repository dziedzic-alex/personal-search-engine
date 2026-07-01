from datetime import datetime

from PIL.ExifTags import Base
from sqlalchemy.dialects import postgresql

from workers.document_processor.image.image_utils import extract_image_metadata


def _source_created_time_from_execute(mock_session) -> datetime:
    statement = mock_session.execute.call_args[0][0]
    params = statement.compile(dialect=postgresql.dialect()).params
    return params["source_created_time"]


def test_extract_image_metadata_uses_exif_datetime(mocker, mock_image_utils_session):
    exif = mocker.MagicMock()
    exif.get_ifd.return_value = {}
    exif.get.return_value = "2025:10:18 21:31:47"
    image = mocker.MagicMock()
    image.getexif.return_value = exif
    image.info = {}

    extract_image_metadata(image, document_id=1)

    mock_image_utils_session.execute.assert_called_once()
    mock_image_utils_session.commit.assert_called_once()
    assert _source_created_time_from_execute(mock_image_utils_session) == datetime(
        2025, 10, 18, 21, 31, 47
    )


def test_extract_image_metadata_prefers_exif_datetime_original(
    mocker, mock_image_utils_session
):
    exif = mocker.MagicMock()
    exif.get_ifd.return_value = {Base.DateTimeOriginal: "2024:05:10 09:07:01"}
    exif.get.return_value = "2025:10:18 21:31:47"
    image = mocker.MagicMock()
    image.getexif.return_value = exif
    image.info = {}

    extract_image_metadata(image, document_id=2)

    assert _source_created_time_from_execute(mock_image_utils_session) == datetime(
        2024, 5, 10, 9, 7, 1
    )


def test_extract_image_metadata_falls_back_to_xmp(mocker, mock_image_utils_session):
    exif = mocker.MagicMock()
    exif.get_ifd.return_value = {}
    exif.get.return_value = None
    image = mocker.MagicMock()
    image.getexif.return_value = exif
    image.info = {
        "xmp": (
            b'<x:xmpmeta xmlns:x="adobe:ns:meta/">'
            b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
            b'<rdf:Description xmlns:xmp="http://ns.adobe.com/xap/1.0/"'
            b' xmp:CreateDate="2025-10-18T21:31:47"/>'
            b"</rdf:RDF></x:xmpmeta>"
        )
    }

    extract_image_metadata(image, document_id=3)

    mock_image_utils_session.execute.assert_called_once()
    assert _source_created_time_from_execute(mock_image_utils_session) == datetime(
        2025, 10, 18, 21, 31, 47
    )


def test_extract_image_metadata_skips_when_no_dates(mocker, mock_image_utils_session):
    exif = mocker.MagicMock()
    exif.get_ifd.return_value = {}
    exif.get.return_value = None
    image = mocker.MagicMock()
    image.getexif.return_value = exif
    image.info = {}

    extract_image_metadata(image, document_id=4)

    mock_image_utils_session.execute.assert_not_called()
    mock_image_utils_session.commit.assert_not_called()
