from typing import Tuple

from PIL import ImageFont
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


def draw_line(
    display: DisplayBase,
    start: Tuple[int, int],
    end: Tuple[int, int],
    color: int = Color.BLACK,
    width: int = 1,
):
    display.draw.line([start, end], fill=color, width=width)
