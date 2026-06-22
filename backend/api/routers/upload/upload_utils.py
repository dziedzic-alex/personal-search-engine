from dataclasses import dataclass
from io import BytesIO

import fitz
from PIL import Image

from shared.content_category import ContentCategory, content_type_to_category
from shared.content_type import ContentType
from shared.image_utils import normalize_image
from shared.s3_client import S3Client

THUMBNAIL_PREFIX = "thumbnail_"
THUMBNAIL_WIDTH = 200
THUMBNAIL_HEIGHT = 200


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


@dataclass
class PersistedFileObjectKeys:
    content_key: str
    thumbnail_key: str


def persist_file(
    s3_client: S3Client,
    filename: str,
    file_data: bytes,
    user_id: int,
    content_type: ContentType,
) -> PersistedFileObjectKeys:
    content_category = content_type_to_category(content_type)
    if content_category == ContentCategory.IMAGE:
        thumbnail = create_image_thumbnail(file_data)
    else:
        thumbnail = create_pdf_thumbnail(file_data)

    thumbnail_filename = THUMBNAIL_PREFIX + filename.split(".")[0] + ".jpg"

    thumbnail_key = s3_client.persist_file(
        thumbnail_filename, user_id, thumbnail, ContentType.JPEG
    )
    try:
        content_key = s3_client.persist_file(filename, user_id, file_data, content_type)
    except Exception as e:
        s3_client.delete_file(thumbnail_key)
        raise e

    return PersistedFileObjectKeys(content_key=content_key, thumbnail_key=thumbnail_key)


def create_image_thumbnail(file_data: bytes) -> bytes:
    image = Image.open(BytesIO(file_data))
    image = normalize_image(image)
    image.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))

    buffer = BytesIO()
    image.save(buffer, format="JPEG")

    return buffer.getvalue()


def create_pdf_thumbnail(file_data: bytes) -> bytes:
    pixel_map = None
    with fitz.open(stream=file_data, filetype="pdf") as pdf:
        pixel_map = pdf.load_page(0).get_pixmap(matrix=fitz.Matrix(1.5, 1.5))

    image = Image.frombytes(
        "RGB", [pixel_map.width, pixel_map.height], pixel_map.samples
    )
    image.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")

    return buffer.getvalue()
