import tkinter
from tkinter import scrolledtext
from enum import Enum


# A class that inherits ScrolledText and matches it to our needs in order to avoid repeating code.
class ScrolledStatusText(scrolledtext.ScrolledText):

    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        for color in TextColor:
            super().tag_config(color, foreground=color.value)

    # Inserts a given string at the end of the text box and automatically scrolls to it.
    def insert(self, text, color):
        super().insert(tkinter.END, str(text) + "\n", color)
        super().yview(tkinter.END)


class TextColor(Enum):
    CONNECTION = 'green'
    DISCONNECTION = 'red'
    # todo: change colors
    FAILURE = 'magenta'
    MESSAGE_SENT = 'yellow'
    KEY = 'blue'
    MESSAGE = 'black'
