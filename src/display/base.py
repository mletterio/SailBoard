from enum import Enum
from typing import Tuple
from PIL import Image, ImageDraw


class Orientation(Enum):
    LANDSCAPE          = 0
    PORTRAIT           = 90
    LANDSCAPE_INVERTED = 180
    PORTRAIT_INVERTED  = 270


class Color:
    WHITE = 0
    BLACK = 1
    RED   = 2


COLOR_RGB = {
    Color.WHITE: (255, 255, 255),
    Color.BLACK: (0,   0,   0),
    Color.RED:   (255, 0,   0),
}


class DisplayBase:
    """Base class for ePaper display with orientation support."""

    def __init__(self, width: int, height: int, orientation: Orientation = Orientation.LANDSCAPE):
        self.native_width  = width
        self.native_height = height
        self.orientation   = orientation
        self._canvas: Image.Image       = None
        self._draw:   ImageDraw.ImageDraw = None
        self.clear()

    @property
    def width(self) -> int:
        if self.orientation in (Orientation.PORTRAIT, Orientation.PORTRAIT_INVERTED):
            return self.native_height
        return self.native_width

    @property
    def height(self) -> int:
        if self.orientation in (Orientation.PORTRAIT, Orientation.PORTRAIT_INVERTED):
            return self.native_width
        return self.native_height

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width, self.height)

    @property
    def canvas(self) -> Image.Image:
        return self._canvas

    @property
    def draw(self) -> ImageDraw.ImageDraw:
        return self._draw

    def clear(self):
        self._canvas = Image.new("P", self.size, Color.WHITE)
        palette = [0] * 768
        for idx, rgb in COLOR_RGB.items():
            palette[idx * 3: idx * 3 + 3] = rgb
        self._canvas.putpalette(palette)
        self._draw = ImageDraw.Draw(self._canvas)

    def get_rotated_image(self) -> Image.Image:
        if self.orientation == Orientation.LANDSCAPE:
            return self._canvas
        return self._canvas.rotate(-self.orientation.value, expand=True)


class InkyDisplay(DisplayBase):
    """ePaper display using the Inky library (Pi only)."""

    def __init__(self, orientation: Orientation = Orientation.LANDSCAPE):
        from inky.auto import auto
        self._inky = auto(ask_user=True, verbose=True)
        self._inky.set_border(self._inky.WHITE)
        super().__init__(self._inky.width, self._inky.height, orientation)

    def show(self):
        rotated = self.get_rotated_image()
        self._inky.set_image(rotated)
        self._inky.show()


class MockDisplay(DisplayBase):
    """Software mock display for local testing."""

    def __init__(self, width: int = 400, height: int = 300, orientation: Orientation = Orientation.LANDSCAPE):
        super().__init__(width, height, orientation)

    def show(self):
        self._canvas.convert('RGB').show()

    def save(self, path: str):
        self._canvas.convert('RGB').save(path)

    def to_rgb(self) -> Image.Image:
        return self._canvas.convert('RGB')
