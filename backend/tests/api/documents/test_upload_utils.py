import uuid
from io import BytesIO

import pytest
from PIL import Image

from api.routers.documents.upload_utils import (
    THUMBNAIL_HEIGHT,
    THUMBNAIL_WIDTH,
    PersistedFileObjectKeys,
    _create_thumbnail,
    persist_file,
    sanitize_content_type,
)
from shared.content_type import ContentType

FILE_GROUP_ID = "550e8400-e29b-41d4-a716-446655440000"


def test_sanitize_content_type_returns_subtype_from_mime_type():
    assert sanitize_content_type("application/pdf", "doc") == "pdf"


def test_sanitize_content_type_returns_extension_for_octet_stream():
    assert sanitize_content_type("application/octet-stream", "photo.heic") == "heic"


def test_persist_file_rolls_back_thumbnail_when_content_upload_fails(mocker):
    mock_s3_client = mocker.MagicMock()
    thumbnail_key = f"1/{FILE_GROUP_ID}/thumbnail"
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
        persist_file(
            mock_s3_client,
            b"image bytes",
            1,
            ContentType.JPEG,
        )

    mock_s3_client.delete_file.assert_called_once_with(thumbnail_key)


def test_persist_file_returns_paired_s3_keys(mocker):
    mock_s3_client = mocker.MagicMock()
    mock_s3_client.persist_file.side_effect = [
        f"1/{FILE_GROUP_ID}/thumbnail",
        f"1/{FILE_GROUP_ID}/content",
    ]
    mocker.patch(
        "api.routers.documents.upload_utils.uuid.uuid4",
        return_value=uuid.UUID(FILE_GROUP_ID),
    )
    mocker.patch(
        "api.routers.documents.upload_utils._create_image_thumbnail",
        return_value=b"thumbnail bytes",
    )

    result = persist_file(
        mock_s3_client,
        b"image bytes",
        1,
        ContentType.PNG,
    )

    assert result == PersistedFileObjectKeys(
        content_key=f"1/{FILE_GROUP_ID}/content",
        thumbnail_key=f"1/{FILE_GROUP_ID}/thumbnail",
    )
    thumbnail_call = mock_s3_client.persist_file.call_args_list[0]
    assert thumbnail_call.args == (
        1,
        b"thumbnail bytes",
        ContentType.JPEG,
        f"{FILE_GROUP_ID}/thumbnail",
    )
    content_call = mock_s3_client.persist_file.call_args_list[1]
    assert content_call.args == (
        1,
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
