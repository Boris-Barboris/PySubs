#   Copyright Alexander Baranin 2016

import sfml
import sfml.graphics as graphics

from sfml.graphics import Font
from sfml.graphics import Text

Logging = None
EngineCore = None

def onLoad(core):
    global EngineCore
    EngineCore = core
    global Logging
    Logging = EngineCore.loaded_modules['engine.Logging']
    Logging.logMessage('TextManager is loading')
    load_font('arial.ttf')

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
