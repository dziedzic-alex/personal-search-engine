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
