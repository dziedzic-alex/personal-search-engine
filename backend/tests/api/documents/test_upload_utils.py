import uuid
from io import BytesIO

import pytest
from PIL import Image
from pillow_heif import register_heif_opener

from api.routers.documents.upload_utils import (
    THUMBNAIL_HEIGHT,
    THUMBNAIL_WIDTH,
    PersistedFileObjectKeys,
    _create_thumbnail,
    convert_heic_or_heif_to_jpeg,
    persist_file_to_s3,
    replace_heic_or_heif_file_type_extension,
    sanitize_content_type,
)
from shared.content_type import ContentType
from tests.api.factories import uid

register_heif_opener()

FILE_GROUP_ID = "550e8400-e29b-41d4-a716-446655440000"
USER_ID = uid(1)


def test_sanitize_content_type_returns_subtype_from_mime_type():
    assert sanitize_content_type("application/pdf", "doc") == "pdf"


def test_sanitize_content_type_returns_extension_for_octet_stream():
    assert sanitize_content_type("application/octet-stream", "photo.heic") == "heic"


def test_sanitize_content_type_returns_extension_when_content_type_is_none():
    assert sanitize_content_type(None, "document.pdf") == "pdf"


def test_sanitize_content_type_returns_extension_when_content_type_has_no_slash():
    assert sanitize_content_type("pdf", "document.pdf") == "pdf"


def test_persist_file_to_s3_rolls_back_thumbnail_when_content_upload_fails(mocker):
    mock_s3_client = mocker.MagicMock()
    thumbnail_key = f"{USER_ID}/{FILE_GROUP_ID}/thumbnail"
    mock_s3_client.persist_file.side_effect = [
        thumbnail_key,
        Exception("s3 error"),
    ]
    mocker.patch(
        "api.routers.documents.upload_utils.uuid.uuid4",
        return_value=uuid.UUID(FILE_GROUP_ID),
    )
    mocker.patch(
        "api.routers.documents.upload_utils._create_image_thumbnail",
        return_value=b"thumbnail bytes",
    )

    with pytest.raises(Exception, match="s3 error"):
        persist_file_to_s3(
            mock_s3_client,
            b"image bytes",
            USER_ID,
            ContentType.JPEG,
        )

    mock_s3_client.delete_file.assert_called_once_with(thumbnail_key)


def test_persist_file_to_s3_returns_paired_s3_keys(mocker):
    mock_s3_client = mocker.MagicMock()
    mock_s3_client.persist_file.side_effect = [
        f"{USER_ID}/{FILE_GROUP_ID}/thumbnail",
        f"{USER_ID}/{FILE_GROUP_ID}/content",
    ]
    mocker.patch(
        "api.routers.documents.upload_utils.uuid.uuid4",
        return_value=uuid.UUID(FILE_GROUP_ID),
    )
    mocker.patch(
        "api.routers.documents.upload_utils._create_image_thumbnail",
        return_value=b"thumbnail bytes",
    )

    result = persist_file_to_s3(
        mock_s3_client,
        b"image bytes",
        USER_ID,
        ContentType.PNG,
    )

    assert result == PersistedFileObjectKeys(
        content_key=f"{USER_ID}/{FILE_GROUP_ID}/content",
        thumbnail_key=f"{USER_ID}/{FILE_GROUP_ID}/thumbnail",
    )
    thumbnail_call = mock_s3_client.persist_file.call_args_list[0]
    assert thumbnail_call.args == (
        USER_ID,
        b"thumbnail bytes",
        ContentType.JPEG,
        f"{FILE_GROUP_ID}/thumbnail",
    )
    content_call = mock_s3_client.persist_file.call_args_list[1]
    assert content_call.args == (
        USER_ID,
        b"image bytes",
        ContentType.PNG,
        f"{FILE_GROUP_ID}/content",
    )


def test_create_thumbnail():
    image = Image.new("RGB", (2000, 1500))

    thumbnail_bytes = _create_thumbnail(image)
    thumbnail = Image.open(BytesIO(thumbnail_bytes))

    assert thumbnail.format == "JPEG"
    assert thumbnail.width <= THUMBNAIL_WIDTH
    assert thumbnail.height <= THUMBNAIL_HEIGHT


def _heic_bytes(size: tuple[int, int] = (32, 24), mode: str = "RGB") -> bytes:
    source = Image.new(
        mode, size, color=(10, 20, 30) if mode == "RGB" else (10, 20, 30, 255)
    )
    source_buffer = BytesIO()
    source.save(source_buffer, format="HEIF")
    return source_buffer.getvalue()


def test_convert_heic_or_heif_to_jpeg_returns_jpeg_bytes():
    jpeg_bytes = convert_heic_or_heif_to_jpeg(_heic_bytes())
    converted = Image.open(BytesIO(jpeg_bytes))

    assert converted.format == "JPEG"
    assert converted.size == (32, 24)


def test_convert_heic_or_heif_to_jpeg_normalizes_image(mocker):
    normalize_image = mocker.patch(
        "api.routers.documents.upload_utils.normalize_image",
        side_effect=lambda image: image.convert("RGB"),
    )

    jpeg_bytes = convert_heic_or_heif_to_jpeg(_heic_bytes(size=(16, 16), mode="RGBA"))

    normalize_image.assert_called_once()
    converted = Image.open(BytesIO(jpeg_bytes))
    assert converted.format == "JPEG"
    assert converted.mode == "RGB"


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("photo.heic", "photo.jpg"),
        ("photo.heif", "photo.jpg"),
        ("photo.HEIC", "photo.jpg"),
        ("photo.HEIF", "photo.jpg"),
        ("vacation.photo.heic", "vacation.photo.jpg"),
        ("already.jpg", "already.jpg"),
        ("document.pdf", "document.pdf"),
        ("noextension", "noextension"),
    ],
)
def test_replace_heic_or_heif_file_type_extension(filename, expected):
    assert replace_heic_or_heif_file_type_extension(filename) == expected
