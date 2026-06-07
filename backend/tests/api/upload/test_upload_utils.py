from api.routers.upload.upload_utils import sanitize_content_type


def test_sanitize_content_type_returns_subtype_from_mime_type():
    assert sanitize_content_type("application/pdf", "doc") == "pdf"


def test_sanitize_content_type_returns_extension_for_octet_stream():
    assert sanitize_content_type("application/octet-stream", "photo.heic") == "heic"
