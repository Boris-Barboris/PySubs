#   Copyright Alexander Baranin 2016

import time
import sys

from engine.Reloadable import reloadable

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('Label', 'engine.ui.Label'))

_subscribe_modules = [
    'engine.ui.Label']

from engine.EngineCore import handle_imports
from sfml.system import Vector2

handle_imports(sys.modules[__name__])

def onLoad(core):
    Logging.logMessage('FPSLabel is loading')

def onUnload():
    Logging.logMessage('FPSLabel is unloading')


@reloadable
class FPSLabel(Label.LabelObject):
    def __init__(self, proxy):
        super(FPSLabel._get_cls(), self).__init__(proxy)
        self.avg_fps = 60.0
        self.time_hp = time.clock()
        self.label.character_size = 20

    def run(self):
        frame_time = time.clock() - self.time_hp
        self.time_hp += frame_time
        self.avg_fps = 0.8 * self.avg_fps + 0.2 / frame_time
        self.label.string = "{0:.1f}".format(self.avg_fps)

    def _reload(self, other, proxy):
        super(FPSLabel._get_cls(), self)._reload(other, proxy)
        self.avg_fps = other.avg_fps
        self.time_hp = other.time_hp
        self.transform.lposition = Vector2(0.0, 0.0)