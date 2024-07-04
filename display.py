import sys
from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw
from font_source_serif_pro import SourceSerifProSemibold
from font_source_sans_pro import SourceSansProSemibold


class Display:

    def __init__(self):
        self.inky_display = auto(ask_user=True, verbose=True)
        self.inky_display.set_border(self.inky_display.WHITE)
        self.img = Image.new("P", (self.inky_display.width, self.inky_display.width))
        self.draw = ImageDraw.Draw(self.img)
        self.serif_font = ImageFont.truetype(SourceSerifProSemibold, 32)

    def clear_canvas(self):
        self.img = Image.new("P", (self.inky_display.width, self.inky_display.height))
        self.draw = ImageDraw.Draw(self.img)

    def write_header(self):
        self.draw.multiline_text((10, 5), "Boston Harbor Forcast",
                                 fill=self.inky_display.RED,
                                 font=self.serif_font, align="left")

    def write_info(self):
        self.draw.multiline_text((10, 40), "NO DATA",
                                 fill=self.inky_display.RED,
                                 font=self.serif_font, align="left")

    def update_display(self):
        self.inky_display.set_image(self.img)
        self.inky_display.show()
