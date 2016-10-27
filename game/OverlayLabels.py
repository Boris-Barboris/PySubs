#   Copyright Alexander Baranin 2016


from sfml.graphics import *
from sfml.system import *

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'))

def onLoad(core):
    Logging.logMessage('OverlayLabels module is loading')

def onUnload():
    Logging.logMessage('OverlayLabels module is unloading')


class submarine_label_class:
    def __init__(self):
        self.shapes = []
        rect1 = RectangleShape()
        rect1.texture = None
        rect1.fill_color = Color(50, 50, 255, 255)
        rect1.outline_thickness = 0
        rect1.size = (3.0, 8.0)
        rect1.position = (-10.0, -4.0)
        rect1.origin = (0.0, 0.0)
        self.shapes.append(rect1)

        rect1 = RectangleShape()
        rect1.texture = None
        rect1.fill_color = Color(50, 50, 255, 255)
        rect1.outline_thickness = 0
        rect1.size = (20.0, 3.0)
        rect1.position = (-10.0, 1.0)
        rect1.origin = (0.0, 0.0)
        self.shapes.append(rect1)

        rect1 = RectangleShape()
        rect1.texture = None
        rect1.fill_color = Color(50, 50, 255, 255)
        rect1.outline_thickness = 0
        rect1.size = (3.0, 8.0)
        rect1.position = (7.0, -4.0)
        rect1.origin = (0.0, 0.0)
        self.shapes.append(rect1)

submarine_label = submarine_label_class()