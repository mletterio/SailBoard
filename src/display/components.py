from typing import Tuple

from PIL import Image, ImageFont
from font_source_serif_pro import SourceSerifProSemibold
from font_source_sans_pro import SourceSansProSemibold

from .base import DisplayBase, Color


class Fonts:
    """Cached font loader."""

    _cache = {}

    @classmethod
    def serif(cls, size: int) -> ImageFont.FreeTypeFont:
        key = ('serif', size)
        if key not in cls._cache:
            cls._cache[key] = ImageFont.truetype(SourceSerifProSemibold, size)
        return cls._cache[key]

    @classmethod
    def sans(cls, size: int) -> ImageFont.FreeTypeFont:
        key = ('sans', size)
        if key not in cls._cache:
            cls._cache[key] = ImageFont.truetype(SourceSansProSemibold, size)
        return cls._cache[key]


def draw_text(
    display: DisplayBase,
    pos: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    color: int = Color.BLACK,
    anchor: str = "la",
):
    display.draw.text(pos, text, fill=color, font=font, anchor=anchor)


def paste_icon(
    display: DisplayBase,
    pos: Tuple[int, int],
    icon_path: str,
    size: int = 32,
    rotate_deg: float = 0,
    expand: bool = False,
    color: int = Color.BLACK,
):
    icon = Image.open(icon_path).convert("RGBA")
    icon = icon.resize((size, size), Image.LANCZOS)
    if rotate_deg:
        icon = icon.rotate(-rotate_deg, resample=Image.BICUBIC, expand=expand)
    tile = Image.new("P", icon.size, color)
    tile.putpalette(display.canvas.getpalette())
    alpha = icon.split()[3].point(lambda a: 255 if a > 128 else 0)
    display.canvas.paste(tile, pos, alpha)