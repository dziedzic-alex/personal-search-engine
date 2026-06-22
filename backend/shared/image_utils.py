from PIL import Image, ImageOps


def normalize_image(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    if image.mode not in ["RGB", "L"]:
        image = image.convert("RGB")
    return image
