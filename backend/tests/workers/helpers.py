from io import BytesIO
from unittest.mock import MagicMock

from PIL import Image


def make_image(width: int = 128, height: int = 128) -> Image.Image:
    return Image.new("RGB", (width, height))


def make_png_image_bytes(width: int = 100, height: int = 100) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (width, height)).save(buffer, format="PNG")
    return buffer.getvalue()


def added_embeddings(session):
    return [call.args[0] for call in session.add.call_args_list]


def make_page(*, text_blocks=(), images=(), page_number=0):
    page = MagicMock()
    page.get_text_blocks.return_value = [
        (0, 0, 100, 100, text, 0, 0) for text in text_blocks
    ]
    page.get_images.return_value = list(images)
    page.number = page_number
    pixels = MagicMock()
    pixels.width = 100
    pixels.height = 100
    pixels.samples = b"\xff" * (100 * 100 * 3)
    page.get_pixmap.return_value = pixels
    return page


def make_document(pages):
    document = MagicMock()
    document.__iter__ = MagicMock(return_value=iter(pages))
    return document
