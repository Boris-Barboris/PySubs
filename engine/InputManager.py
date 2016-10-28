#   Copyright Alexander Baranin 2016

# Here we introduce the concept of input focus. All input events are
# first routed to active input reciever, wich performs some actions according
# to it's logic and then returns True if it lets the event to go through to
# global event handlers. Those are non-exclusive and handle all events that are
# left. State in which no active reciever is perfectly valid.

import sfml
from sfml.graphics import Rectangle
from sfml.system import Vector2

from engine.Reloadable import reloadable
from engine.GameObject import Component
from engine.SpacialHash import Fixed2DHash

import weakref

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('IOBroker', 'engine.IOBroker'))

def onLoad(core):
    Logging.logMessage('InputManager is loading')
    global composer
    inputManager = InputManager._persistent('InputManager.inputManager')

def onUnload():
    Logging.logMessage('InputManager is unloading')


inputManager = None

@reloadable
class InputManager:
    pass