def sanitize_content_type(content_type: str, filename: str) -> str:
    sanitized = content_type.split("/")[1]
    if sanitized == "octet-stream":
        return filename.split(".").pop().lower()
    return sanitized


ALLOWED_CONTENT_TYPES = [
    "pdf",
    "jpeg",
    "jpg",
    "png",
    "webp",
    "heic",
    "heif",
]

def is_allowed_content_type(content_type: str) -> bool:
    return content_type in ALLOWED_CONTENT_TYPES
