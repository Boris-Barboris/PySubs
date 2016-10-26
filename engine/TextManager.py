#   Copyright Alexander Baranin 2016

import sfml
import sfml.graphics as graphics
import traceback

from sfml.graphics import Font
from sfml.graphics import Text

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'))

def onLoad(core):
    Logging.logMessage('TextManager is loading')
    load_font('calibri.ttf')

def onUnload():
    Logging.logMessage('TextManager is unloading')


# global loaded fonts dictionary
loaded_fonts = {}


def load_font(font_name):
    try:
        if font_name in loaded_fonts:
            return loaded_fonts[font_name]
        f = Font.from_file(font_name)
        loaded_fonts[font_name] = f
        return f
    except IOError as ex:
        Logging.logMessage('cannot load font ' + font_name + 
                           ':\n' + str(ex))
        traceback.print_exc()
