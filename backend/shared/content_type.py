import enum


class ContentType(enum.StrEnum):
    PDF = "pdf"
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"
    HEIC = "heic"
    HEIF = "heif"


IMAGE_CONTENT_TYPES = frozenset(
    {
        ContentType.JPEG,
        ContentType.JPG,
        ContentType.PNG,
        ContentType.WEBP,
        ContentType.HEIC,
        ContentType.HEIF,
    }
)

IMAGE_CONTENT_TYPE_VALUES = frozenset(
    content_type.value for content_type in IMAGE_CONTENT_TYPES
)

_CONTENT_TYPE_TO_MIME: dict[ContentType, str] = {
    ContentType.PDF: "application/pdf",
    ContentType.JPEG: "image/jpeg",
    ContentType.JPG: "image/jpeg",
    ContentType.PNG: "image/png",
    ContentType.WEBP: "image/webp",
    ContentType.HEIC: "image/heic",
    ContentType.HEIF: "image/heif",
}


def content_type_to_mime_type(content_type: ContentType) -> str:
    return _CONTENT_TYPE_TO_MIME[content_type]
