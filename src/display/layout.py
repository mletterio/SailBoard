"""BoardLayout — stacked Header / Forecast / Tides layout for ePaper display."""

import os
import textwrap
from datetime import datetime
from typing import Optional

import pandas as pd

from .base import DisplayBase, Color
from .components import Fonts, draw_text, paste_icon
from .vstack import VStack

MARGIN = 10
ICONS_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")

_WIND_DIR_DEG = {
    'N': 0,   'NNE': 22,  'NE': 45,  'ENE': 67,
    'E': 90,  'ESE': 112, 'SE': 135, 'SSE': 157,
    'S': 180, 'SSW': 202, 'SW': 225, 'WSW': 247,
    'W': 270, 'WNW': 292, 'NW': 315, 'NNW': 337,
}


# ---------------------------------------------------------------------------
# Drawing helpers for each section
# ---------------------------------------------------------------------------

HEADER_H  = 58
FOOTER_H  = 24
ROW_H     = 72
TIDE_ROW_H = 20


def _draw_header(display: DisplayBase, y: int, h: int):
    font = Fonts.serif(35)
    text_y = y + 4
    draw_text(display, (MARGIN, text_y), "Boston Harbor", font, Color.RED)

    text_w = int(display.draw.textlength("Boston Harbor", font=font))
    ascent, _ = font.getmetrics()
    anchor_sz = 28
    icon_y = text_y + ascent - anchor_sz
    paste_icon(display, (MARGIN + text_w + 8, max(0, icon_y)),
                       os.path.join(ICONS_DIR, "anchor-simple.png"),
                       size=anchor_sz, color=Color.BLACK)


def _draw_footer(display: DisplayBase, y: int, h: int, updated_at=None):
    ts = (updated_at or datetime.now()).strftime('%H:%M:%S')
    draw_text(display, (MARGIN, y + 2),
              f"Updated: {ts}", Fonts.sans(15), Color.BLACK)


def _make_forecast_drawer(df: pd.DataFrame):
    """Return a draw callable for the forecast section."""

    def _draw(display: DisplayBase, y: int, h: int):
        if df.empty:
            return

        arrow_path = os.path.join(ICONS_DIR, "nav-arrow.png")
        arrow_sz = 24
        expanded = int(arrow_sz * 1.42) + 2
        arrow_right = display.width - MARGIN
        arrow_cx = arrow_right - expanded // 2

        wind_font = Fonts.sans(20)
        wind_text_right = arrow_cx - expanded // 2 - 6

        row_h = min(ROW_H, h // min(3, len(df)))

        for _, row in df.head(3).iterrows():
            name  = str(row.get('period_name', 'Unknown'))[:15]
            temp  = row.get('temperature_f')
            speed = float(row.get('wind_speed_avg_kts') or 0)
            gust  = float(row.get('wind_gust_max_kts') or 0)
            dirn  = str(row.get('wind_direction') or '')
            cond  = str(row.get('short_forecast') or '')

            # --- Left column ---
            # Line 1: period name
            draw_text(display, (MARGIN, y), name,
                      Fonts.sans(20), Color.BLACK)
            # Line 2: temperature
            if pd.notna(temp):
                draw_text(display, (MARGIN, y + 24), f"{int(temp)}°F",
                          Fonts.sans(16), Color.BLACK)
            # Line 3: conditions — aggressive wrap
            avail_w = wind_text_right - MARGIN - 8
            left_col_chars = max(8, avail_w // 9)
            cond_line = (textwrap.wrap(cond, width=left_col_chars) or [''])[0]
            draw_text(display, (MARGIN, y + 44), cond_line,
                      Fonts.sans(14), Color.BLACK)

            # --- Right column: wind text + arrow, top-aligned to period ---
            # Arrow top-aligned with the period name baseline area
            arrow_y = y + 2
            wind_deg = _WIND_DIR_DEG.get(dirn.upper().strip(), 0)
            paste_icon(
                display,
                (arrow_cx - expanded // 2, arrow_y),
                arrow_path, size=arrow_sz,
                rotate_deg=wind_deg, expand=True)

            # Speed stacked above direction, right-aligned to left of arrow
            draw_text(display,
                      (wind_text_right, arrow_y + 2),
                      f"{speed:.0f}/{gust:.0f}kt",
                      wind_font, Color.BLACK, anchor="rt")
            draw_text(display,
                      (wind_text_right, arrow_y + 20),
                      dirn,
                      wind_font, Color.BLACK, anchor="rt")

            y += row_h

    return _draw


def _make_tides_drawer(tides_df: pd.DataFrame):
    """Return a draw callable for the tides section."""

    def _draw(display: DisplayBase, y: int, h: int):
        num_rows = min(4, len(tides_df))
        table_h = num_rows * TIDE_ROW_H

        title_font = Fonts.serif(22)
        icon_sz = 24

        # --- Right column: tide table ---
        title_w = int(display.draw.textlength("Tides", font=title_font))
        table_x = MARGIN + max(title_w, icon_sz) + 18
        table_y = y + max(0, (h - table_h) // 2)

        # --- Left column: title + icon, top-aligned with the table ---
        title_ascent = title_font.getmetrics()[0]
        draw_text(display, (MARGIN, table_y), "Tides", title_font, Color.RED)
        paste_icon(display, (MARGIN, table_y + title_ascent + 12),
                   os.path.join(ICONS_DIR, "waves.png"),
                   size=icon_sz, color=Color.BLACK)

        for _, row in tides_df.head(num_rows).iterrows():
            time_val = row.name if hasattr(row.name, 'strftime') else row.get('time')
            time_str = (time_val.strftime('%a %H:%M')
                        if hasattr(time_val, 'strftime') else str(time_val)[:10])
            tide_type = row.get('tide_type', '').upper()[:1]
            height = row.get('tide_height_m', 0)
            draw_text(display, (table_x, table_y),
                      f"{time_str}  {tide_type}  {height:.1f}m",
                      Fonts.sans(14), Color.BLACK)
            table_y += TIDE_ROW_H

    return _draw


# ---------------------------------------------------------------------------
# Main layout class
# ---------------------------------------------------------------------------

class BoardLayout:
    """Renders the complete SailBoard display (300 wide × 400 tall, portrait).

    Uses a VStack to divide vertical space:
      header  (fixed 48px)
      forecast (fixed: 3 × row_h)
      gap      (flex — splits remaining space with tides gap)
      tides    (fixed: title/icon height or 4 rows)
      gap      (flex)
      footer   (fixed 24px)
    """

    def __init__(self, display: DisplayBase):
        self.display = display

    def render(
        self,
        forecast_df: pd.DataFrame,
        tides_df: Optional[pd.DataFrame] = None,
        updated_at: datetime = None,
    ):
        self.display.clear()

        n_forecast = min(3, len(forecast_df)) if not forecast_df.empty else 0
        forecast_h = n_forecast * ROW_H

        has_tides = tides_df is not None and not tides_df.empty
        n_tides = min(4, len(tides_df)) if has_tides else 0
        tides_h = max(n_tides * TIDE_ROW_H, 70) if has_tides else 0

        stack = VStack(self.display.height)
        stack.add("header", height=HEADER_H, draw=_draw_header)
        stack.add("forecast", height=forecast_h,
                  draw=_make_forecast_drawer(forecast_df))
        stack.add("mid_gap", flex=1)
        if has_tides:
            stack.add("tides", height=tides_h,
                      draw=_make_tides_drawer(tides_df))
            stack.add("bot_gap", flex=1)
        stack.add("footer", height=FOOTER_H,
                  draw=lambda d, y, h: _draw_footer(d, y, h, updated_at))
        stack.resolve()
        stack.render(self.display)