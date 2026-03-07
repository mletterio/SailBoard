"""BoardLayout — the single place to control what appears on screen and where."""

from datetime import datetime
from typing import Optional

import pandas as pd

from .base import DisplayBase, Color
from .components import Fonts, draw_text
from .harbor_map import HarborMap


class BoardLayout:
    """Renders the complete SailBoard display.

    Layout (landscape):
    ┌─────────────────────────────────────┐
    │  HEADER  title + timestamp          │
    ├──────────────────┬──────────────────┤
    │  FORECAST        │  TIDES           │
    │  3 days, uniform │  upcoming H/L    │
    ├──────────────────┴──────────────────┤
    │  MAP  Mapbox + wind arrow           │
    └─────────────────────────────────────┘
    """

    MARGIN        = 6
    HEADER_H      = 60    # includes padding below title
    MAP_FRACTION  = 0.35
    FORECAST_DAYS = 3
    TIDE_ROWS     = 4

    def __init__(self, display: DisplayBase):
        self.display = display
        self.map_h = int(display.height * self.MAP_FRACTION)
        self.col_x = display.width // 2    # x where right column starts

    def render(
        self,
        forecast_df: pd.DataFrame,
        tides_df: Optional[pd.DataFrame] = None,
        wind_dir: str = None,
        wind_speed: float = None,
        updated_at: datetime = None,
    ):
        self.display.clear()
        self._draw_header(updated_at)
        self._draw_forecast(forecast_df, y=self.HEADER_H, x=self.MARGIN)
        if tides_df is not None and not tides_df.empty:
            self._draw_tides(tides_df, y=self.HEADER_H, x=self.col_x)
        self._draw_map(wind_dir, wind_speed)

    def _draw_header(self, updated_at: datetime = None):
        draw_text(self.display, (self.MARGIN, 2), "Boston Harbor", Fonts.sans(28), Color.RED)
        ts = (updated_at or datetime.now()).strftime('%H:%M')
        draw_text(self.display, (self.MARGIN, 36), f"Updated: {ts}", Fonts.sans(14))

    def _draw_forecast(self, df: pd.DataFrame, y: int, x: int):
        if df.empty:
            return
        font = Fonts.sans(16)
        for _, row in df.head(self.FORECAST_DAYS).iterrows():
            name  = row.get('period_name', 'Unknown')
            speed = row.get('wind_speed_avg_kts', 0) or 0
            gust  = row.get('wind_gust_max_kts', 0) or 0
            dirn  = row.get('wind_direction', '')
            cond  = row.get('short_forecast', '')
            draw_text(self.display, (x, y),      name[:10],                        font, Color.RED)
            draw_text(self.display, (x, y + 18), f"{speed:.0f}/{gust:.0f}kt {dirn}", font)
            draw_text(self.display, (x, y + 36), cond[:18],                        Fonts.sans(13))
            y += 58

    def _draw_tides(self, tides_df: pd.DataFrame, y: int, x: int):
        draw_text(self.display, (x, y), "Tides", Fonts.sans(16), Color.RED)
        y += 20
        font = Fonts.sans(14)
        for _, row in tides_df.head(self.TIDE_ROWS).iterrows():
            time_val  = row.name if hasattr(row.name, 'strftime') else row.get('time')
            time_str  = time_val.strftime('%a %H:%M') if hasattr(time_val, 'strftime') else str(time_val)[:10]
            tide_type = row.get('tide_type', '').upper()[:1]
            height    = row.get('tide_height_m', 0)
            draw_text(self.display, (x, y), f"{time_str} {tide_type} {height:.1f}m", font)
            y += 18

    def _draw_map(self, wind_dir: str = None, wind_speed: float = None):
        map_y = self.display.height - self.map_h
        HarborMap(self.display, pos=(0, map_y), size=(self.display.width, self.map_h)).render(
            wind_direction=wind_dir, wind_speed=wind_speed
        )
