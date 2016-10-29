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

handle_imports(sys.modules[__name__])

def onLoad(core):
    Logging.logMessage('FPSLabel is loading')

def onUnload():
    Logging.logMessage('FPSLabel is unloading')


@reloadable
class FPSLabel(Label.LabelObject):
    def __init_rld__(self, proxy):
        super(FPSLabel._get_cls(), self).__init_rld__(proxy)
        self.avg_fps = 60.0
        self.time_hp = time.clock()
        self.text.character_size = 20

    def run(self):
        frame_time = time.clock() - self.time_hp
        self.time_hp += frame_time
        self.avg_fps = 0.8 * self.avg_fps + 0.2 / frame_time
        self.text.string = "{0:.1f}".format(self.avg_fps)

    def _reload(self, other):
        super(FPSLabel._get_cls(), self)._reload(other)
        self.avg_fps = other.avg_fps
        self.time_hp = other.time_hp
        #self.text.character_size = 20