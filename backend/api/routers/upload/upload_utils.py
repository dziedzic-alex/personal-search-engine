from shared.content_type import ContentType


def sanitize_content_type(content_type: str, filename: str) -> str:
    sanitized = content_type.split("/")[1]
    if sanitized == "octet-stream":
        return filename.split(".").pop().lower()
    return sanitized


def is_allowed_content_type(content_type: str) -> bool:
    try:
        ContentType(content_type)
    except ValueError:
        return False
    else:
        return True
