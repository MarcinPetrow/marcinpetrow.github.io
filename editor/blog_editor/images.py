from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil

from PIL import Image, ImageOps


@dataclass
class ImageEdits:
    width: int | None = None
    height: int | None = None
    rotate: int = 0
    crop_left: int = 0
    crop_top: int = 0
    crop_right: int = 0
    crop_bottom: int = 0
    output_format: str | None = None
    quality: int = 88


def safe_image_name(name: str) -> str:
    stem = re.sub(r'-+', '-', re.sub(r'[^a-zA-Z0-9]+', '-', Path(name).stem)).strip('-').lower()
    suffix = Path(name).suffix.lower()
    return f'{stem or "image"}{suffix}'


def unique_destination(folder: Path, filename: str) -> Path:
    candidate = folder / filename
    counter = 2
    while candidate.exists():
        candidate = folder / f'{Path(filename).stem}-{counter}{Path(filename).suffix}'
        counter += 1
    return candidate


def import_image(root: Path, source: Path, prefix: str = '') -> tuple[Path, str]:
    folder = root / 'public' / 'images'
    folder.mkdir(parents=True, exist_ok=True)
    filename = safe_image_name(f'{prefix}-{source.name}' if prefix else source.name)
    destination = unique_destination(folder, filename)
    shutil.copy2(source, destination)
    return destination, f'/images/{destination.name}'


def edit_image(path: Path, edits: ImageEdits) -> Path:
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source)
        width, height = image.size
        box = (
            max(0, edits.crop_left),
            max(0, edits.crop_top),
            max(1, width - max(0, edits.crop_right)),
            max(1, height - max(0, edits.crop_bottom)),
        )
        if box[0] >= box[2] or box[1] >= box[3]:
            raise ValueError('Crop margins remove the whole image.')
        if box != (0, 0, width, height):
            image = image.crop(box)
        if edits.rotate:
            image = image.rotate(-edits.rotate, expand=True)
        if edits.width or edits.height:
            target_width = edits.width or round(image.width * edits.height / image.height)
            target_height = edits.height or round(image.height * edits.width / image.width)
            if target_width <= 0 or target_height <= 0:
                raise ValueError('Image dimensions must be positive.')
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        output = path
        if edits.output_format:
            suffix = f'.{edits.output_format.lower().replace("jpeg", "jpg")}'
            output = path.with_suffix(suffix)
        fmt = (edits.output_format or output.suffix.lstrip('.')).upper().replace('JPG', 'JPEG')
        if fmt == 'JPEG' and image.mode not in ('RGB', 'L'):
            background = Image.new('RGB', image.size, 'white')
            if image.mode == 'RGBA':
                background.paste(image, mask=image.getchannel('A'))
            else:
                background.paste(image.convert('RGB'))
            image = background
        save_options = {'quality': edits.quality, 'optimize': True} if fmt in {'JPEG', 'WEBP'} else {}
        image.save(output, format=fmt, **save_options)
    return output
