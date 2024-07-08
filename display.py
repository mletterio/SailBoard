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
        self.serif_font = ImageFont.truetype(SourceSerifProSemibold, 35)
        self.sans_font = ImageFont.truetype(SourceSansProSemibold, 25)
        self.sans_font_small = ImageFont.truetype(SourceSansProSemibold, 18)


    def clear_canvas(self):
        self.img = Image.new("P", (self.inky_display.width, self.inky_display.height))
        self.draw = ImageDraw.Draw(self.img)

    def write_header(self):
        self.draw.multiline_text((2, 0), "Boston Harbor",
                                 fill=self.inky_display.RED,
                                 font=self.serif_font, align="left")

    def write_info(self, weather_data):
        self.draw.multiline_text((2, 50), weather_data,
                                 fill=self.inky_display.BLACK,
                                 font=self.sans_font, align="left")

    def write_timestamp(self, time):
        self.draw.multiline_text((2, 280), time,
                                 fill=self.inky_display.BLACK,
                                 font=self.sans_font_small, align="left")

    def update_display(self):
        self.inky_display.set_image(self.img)
        self.inky_display.show()
