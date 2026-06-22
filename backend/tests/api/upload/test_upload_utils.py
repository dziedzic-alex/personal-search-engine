import pytest

from api.routers.upload.upload_utils import (
    PersistedFileObjectKeys,
    sanitize_content_type,
    persist_file,
)
from shared.content_type import ContentType


def test_sanitize_content_type_returns_subtype_from_mime_type():
    assert sanitize_content_type("application/pdf", "doc") == "pdf"


def test_sanitize_content_type_returns_extension_for_octet_stream():
    assert sanitize_content_type("application/octet-stream", "photo.heic") == "heic"


def test_persist_file_rolls_back_thumbnail_when_content_upload_fails(mocker):
    mock_s3_client = mocker.MagicMock()
    mock_s3_client.persist_file.side_effect = [
        "1/thumbnail_test.jpg",
        Exception("s3 error"),
    ]
    mocker.patch(
        "api.routers.upload.upload_utils.create_image_thumbnail",
        return_value=b"thumbnail bytes",
    )

    with pytest.raises(Exception, match="s3 error"):
        persist_file(
            mock_s3_client,
            "test.jpg",
            b"image bytes",
            1,
            ContentType.JPEG,
        )

    mock_s3_client.delete_file.assert_called_once_with("1/thumbnail_test.jpg")


def test_persist_file_returns_s3_keys(mocker):
    mock_s3_client = mocker.MagicMock()
    mock_s3_client.persist_file.side_effect = ["1/thumbnail_test.jpg", "1/test.png"]

    mocker.patch(
        "api.routers.upload.upload_utils.create_image_thumbnail",
        return_value=b"thumbnail bytes",
    )

    result = persist_file(
        mock_s3_client,
        "test.png",
        b"image bytes",
        1,
        ContentType.PNG,
    )

    assert result == PersistedFileObjectKeys(
        content_key="1/test.png",
        thumbnail_key="1/thumbnail_test.jpg",
    )
    assert mock_s3_client.persist_file.call_args_list[0].args[3] == ContentType.JPEG
    assert mock_s3_client.persist_file.call_args_list[1].args[3] == ContentType.PNG
