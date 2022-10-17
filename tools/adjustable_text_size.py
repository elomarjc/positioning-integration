import tkinter  # Python GUI tool, to open a window
import tkinter.font


# according to the width limit and height limit, automatically adjust the size of the text
class adjustable_text():

    def __init__(self, text: str, text_font: tkinter.font.Font):
        self.text = text
        self.text_font = text_font

    def adjust_font(self, width, height):
        size = 1
        self.text_font.configure(size=size)
        # measure can get the width of the text, metrics("linespace") can get the height of the text
        while self.text_font.measure(
                self.text) < width and self.text_font.metrics(
                    "linespace") < height:
            size += 1
            self.text_font.configure(size=size)
        if size > 1:
            size -= 1
            self.text_font.configure(size=size)
