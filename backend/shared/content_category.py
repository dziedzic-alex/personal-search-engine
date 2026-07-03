import enum

from shared.content_type import (
    IMAGE_CONTENT_TYPE_VALUES,
    IMAGE_CONTENT_TYPES,
    ContentType,
)


class ContentCategory(enum.StrEnum):
    PDF = "pdf"
    IMAGE = "image"


def content_type_to_category(content_type: str | ContentType) -> ContentCategory:
    if isinstance(content_type, ContentType):
        content_type = content_type.value

    if content_type == ContentType.PDF.value:
        return ContentCategory.PDF

    if content_type in IMAGE_CONTENT_TYPE_VALUES:
        return ContentCategory.IMAGE

    raise ValueError(f"Unsupported content type: {content_type}")


def get_content_types_for_category(category: ContentCategory) -> list[ContentType]:
    if category == ContentCategory.PDF:
        return [ContentType.PDF]
    elif category == ContentCategory.IMAGE:
        return list(IMAGE_CONTENT_TYPES)
