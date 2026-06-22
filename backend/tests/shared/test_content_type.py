import pytest

from shared.content_type import ContentType, content_type_to_mime_type


@pytest.mark.parametrize("content_type", list(ContentType))
def test_every_content_type_has_a_mime_mapping(content_type):
    mime_type = content_type_to_mime_type(content_type)
    assert "/" in mime_type
