import xml.etree.ElementTree as ET
from datetime import datetime

from PIL import Image
from PIL.ExifTags import Base
from sqlalchemy import update

from db.models.document import Document
from db.session import SessionLocal

EXIF_DATETIME_FORMAT = "%Y:%m:%d %H:%M:%S"
XMP_NS = "http://ns.adobe.com/xap/1.0/"
PHOTOSHOP_NS = "http://ns.adobe.com/photoshop/1.0/"
XMP_DATE_FIELDS = (
    (XMP_NS, "CreateDate"),
    (PHOTOSHOP_NS, "DateCreated"),
    (XMP_NS, "ModifyDate"),
)


def _parse_exif_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.strptime(value, EXIF_DATETIME_FORMAT)
    except ValueError:
        return None


def _parse_xmp_datetime(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_source_created_time_from_exif(image: Image.Image) -> datetime | None:
    exif = image.getexif()
    if not exif:
        return None

    exif_ifd = exif.get_ifd(Base.ExifOffset)
    for tag in (Base.DateTimeOriginal, Base.DateTimeDigitized):
        source_created_time = _parse_exif_datetime(exif_ifd.get(tag))
        if source_created_time is not None:
            return source_created_time

    return _parse_exif_datetime(exif.get(Base.DateTime))


def _parse_source_created_time_from_xmp(image: Image.Image) -> datetime | None:
    if not image.info:
        return None

    xmp_metadata = image.info.get("xmp")
    if not xmp_metadata:
        return None

    try:
        root = ET.fromstring(xmp_metadata)
    except ET.ParseError:
        return None

    for namespace, local_name in XMP_DATE_FIELDS:
        qualified_name = f"{{{namespace}}}{local_name}"

        for element in root.iter():
            attribute_value = element.attrib.get(qualified_name)
            if attribute_value:
                source_created_time = _parse_xmp_datetime(attribute_value)
                if source_created_time is not None:
                    return source_created_time

        for element in root.iter(qualified_name):
            if not element.text:
                continue
            source_created_time = _parse_xmp_datetime(element.text)
            if source_created_time is not None:
                return source_created_time

    return None


def extract_image_metadata(image: Image.Image, document_id: int):
    source_created_time = _parse_source_created_time_from_exif(image)

    if source_created_time is None:
        source_created_time = _parse_source_created_time_from_xmp(image)

    if source_created_time is None:
        return

    with SessionLocal() as session:
        session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(source_created_time=source_created_time)
        )
        session.commit()
