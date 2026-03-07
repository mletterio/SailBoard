"""Harbor map renderer with Mapbox Static API and a wind direction arrow."""

import math
from io import BytesIO
from typing import Optional, Tuple

from PIL import Image
import requests

import config
from .base import DisplayBase, Color
from .components import Fonts


_WIND_ANGLES = {
    'N': 270, 'NNE': 292.5, 'NE': 315, 'ENE': 337.5,
    'E': 0,   'ESE': 22.5,  'SE': 45,  'SSE': 67.5,
    'S': 90,  'SSW': 112.5, 'SW': 135, 'WSW': 157.5,
    'W': 180, 'WNW': 202.5, 'NW': 225, 'NNW': 247.5,
}

MAPBOX_API = "https://api.mapbox.com/styles/v1"


class HarborMap:
    """Renders Boston Harbor map from Mapbox with a wind direction arrow overlay."""

    def __init__(self, display: DisplayBase, pos: Tuple[int, int], size: Tuple[int, int]):
        self.display = display
        self.x, self.y = pos
        self.width, self.height = size
        self._map_cache: Optional[Image.Image] = None

    def render(self, wind_direction: str = None, wind_speed: float = None):
        self._draw_map()
        if wind_direction:
            self._draw_wind_arrow(wind_direction)

    def _fetch_map(self) -> Optional[Image.Image]:
        if self._map_cache:
            return self._map_cache

        token = getattr(config, 'MAPBOX_ACCESS_TOKEN', None)
        if not token:
            return None

        style = "mletterio/clyc7axta00zx01qj0si10f12"
        url = (f"{MAPBOX_API}/{style}/static/"
               f"{config.LONGITUDE},{config.LATITUDE},10.35/"
               f"{self.width}x{self.height}")
        try:
            r = requests.get(url, params={'access_token': token, 'attribution': 'false', 'logo': 'false'}, timeout=10)
            if r.status_code == 200:
                self._map_cache = Image.open(BytesIO(r.content)).convert('RGBA')
                return self._map_cache
        except Exception as e:
            print(f"Map fetch error: {e}")
        return None

    def _draw_map(self):
        img = self._fetch_map()
        if img:
            for py in range(self.height):
                for px in range(self.width):
                    r, g, b, a = img.getpixel((px, py))
                    color = Color.WHITE if (a < 128 or r + g + b > 384) else Color.BLACK
                    self.display.canvas.putpixel((self.x + px, self.y + py), color)
        else:
            self.display.draw.rectangle(
                [self.x, self.y, self.x + self.width, self.y + self.height],
                outline=Color.BLACK, width=1,
            )
        credit_y = self.y + self.height - 14
        self.display.draw.text((self.x + 4, credit_y), "© Mapbox", fill=Color.BLACK, font=Fonts.sans(10))

    def _draw_wind_arrow(self, direction: str):
        """Draw a solid triangle pointing in the wind direction, centered on the map."""
        angle = math.radians(_WIND_ANGLES.get(direction.upper(), 0))
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        size = min(self.width, self.height) // 3

        tip_offset = size / math.sqrt(3)
        tip  = (cx + math.cos(angle) * tip_offset,  cy + math.sin(angle) * tip_offset)
        back = [(tip[0] + math.cos(angle + r) * size, tip[1] + math.sin(angle + r) * size)
                for r in (math.radians(150), math.radians(-150))]

        polygon = [(int(tip[0]), int(tip[1])), (int(back[0][0]), int(back[0][1])), (int(back[1][0]), int(back[1][1]))]
        self.display.draw.polygon(polygon, fill=Color.RED)
