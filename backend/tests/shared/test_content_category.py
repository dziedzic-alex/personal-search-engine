import pytest

from shared.content_category import ContentCategory, content_type_to_category
from shared.content_type import ContentType


@pytest.mark.parametrize(
    "content_type",
    [
        ContentType.JPEG,
        ContentType.JPG,
        ContentType.PNG,
        ContentType.WEBP,
        ContentType.HEIC,
        ContentType.HEIF,
        "jpeg",
        "png",
    ],
)
def test_content_type_to_category_returns_image(content_type):
    assert content_type_to_category(content_type) == ContentCategory.IMAGE


def test_content_type_to_category_returns_pdf():
    assert content_type_to_category(ContentType.PDF) == ContentCategory.PDF
    assert content_type_to_category("pdf") == ContentCategory.PDF


def test_content_type_to_category_raises_for_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported content type"):
        content_type_to_category("txt")
