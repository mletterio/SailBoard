"""VStack — simple vertical layout framework for fixed and flexible sections."""

from dataclasses import dataclass
from typing import Callable, List

from .base import DisplayBase


@dataclass
class Section:
    """A named vertical section with a fixed or flexible height."""
    name: str
    height: int = 0         # 0 = flexible (gets share of remaining space)
    flex: float = 0.0       # relative weight when distributing leftover px
    draw: Callable = None   # draw(display, y, height) → None
    _resolved_y: int = 0
    _resolved_h: int = 0


class VStack:
    """Allocates vertical space among fixed and flexible sections.

    Usage:
        stack = VStack(total_height=400)
        stack.add("header",   height=48,  draw=draw_header)
        stack.add("forecast", height=210, draw=draw_forecast)
        stack.add("gap",      flex=1)                         # absorbs leftover
        stack.add("tides",    height=100, draw=draw_tides)
        stack.add("footer",   height=22,  draw=draw_footer)
        stack.resolve()
        stack.render(display)
    """

    def __init__(self, total_height: int):
        self.total = total_height
        self.sections: List[Section] = []

    def add(self, name: str, *, height: int = 0, flex: float = 0,
            draw: Callable = None):
        self.sections.append(Section(name=name, height=height, flex=flex,
                                     draw=draw))
        return self

    def resolve(self):
        fixed = sum(s.height for s in self.sections)
        remaining = max(0, self.total - fixed)
        total_flex = sum(s.flex for s in self.sections) or 1
        y = 0
        for s in self.sections:
            s._resolved_y = y
            if s.flex > 0 and s.height == 0:
                s._resolved_h = int(remaining * s.flex / total_flex)
            else:
                s._resolved_h = s.height
            y += s._resolved_h

    def render(self, display: DisplayBase):
        for s in self.sections:
            if s.draw:
                s.draw(display, s._resolved_y, s._resolved_h)

    def get(self, name: str) -> Section:
        return next(s for s in self.sections if s.name == name)
