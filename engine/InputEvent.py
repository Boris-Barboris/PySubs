#   Copyright Alexander Baranin 2016

from sfml.graphics import View
from sfml.graphics import Rectangle
from sfml.system import Vector2
from engine.Reloadable import reloadable, freeze_module_instances, \
    reload_module_instances, unfreeze_module_instances

Logging = None
EngineCore = None
IOBroker = None

def onLoad(core):
    global EngineCore
    EngineCore = core
    global Logging
    Logging = EngineCore.loaded_modules['engine.Logging']
    global IOBroker
    IOBroker = EngineCore.loaded_modules['engine.IOBroker']
    Logging.logMessage('InputEvent is loading')

def onUnload():
    Logging.logMessage('InputEvent is unloading')


class EventReciever:
    def onMouseEnter(self):
        pass
    def onMouseLeave(self):
        pass
    def onMouseEvent(self, event):
        pass


    
    