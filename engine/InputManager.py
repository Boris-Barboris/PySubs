#   Copyright Alexander Baranin 2016

# Here we introduce the concept of input focus. All input events are
# first routed to active input reciever, wich performs some actions according
# to it's logic and then returns True if it lets the event to go through to
# global(unmanaged) event handlers. Those are non-exclusive and handle all events that are
# left. State in which no active reciever is perfectly valid.
#
# Typical managed event consumer is some UI primitive (Button, window, label,
#   game object collision box...), wich leads us to the concept of z-order.
# Al managed recievers will be split onto 3 ordered layers (World, Overlay, UI).
# World layer components will manage depth on their own (sice they usually tend
# to have their own concept of depth). Other two are ordered by InputManager.

import sfml
from sfml.graphics import Rectangle
from sfml.system import Vector2

from engine.Reloadable import reloadable
from engine.GameObject import Component
from engine.SpacialHash import Fixed2DHash
from engine.OrderedDeque import WeakOrderedDeque

import weakref


_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('IOBroker', 'engine.IOBroker'),
    ('WindowModule', 'engine.WindowModule'))

def onLoad(core):
    Logging.logMessage('InputManager is loading')
    global inputManager
    inputManager = InputManager._persistent('InputManager.inputManager')
    IOBroker.register_handler(handle_event, sfml.window.MouseMoveEvent)
    IOBroker.register_handler(handle_event, sfml.window.MouseWheelEvent)
    IOBroker.register_handler(handle_event, sfml.window.MouseButtonEvent)

def onUnload():
    Logging.logMessage('InputManager is unloading')
    IOBroker.unregister_handler(handle_event, sfml.window.MouseMoveEvent)
    IOBroker.unregister_handler(handle_event, sfml.window.MouseWheelEvent)
    IOBroker.unregister_handler(handle_event, sfml.window.MouseButtonEvent)


inputManager = None

@reloadable
class InputManager:
    def __init__(self):
        self.uiManaged = WeakOrderedDeque()
        self.uiHash = Fixed2DHash(WindowModule.app_window.size(), (5, 4))
        self.overlayManaged = WeakOrderedDeque()
        self.overlayHash = Fixed2DHash(WindowModule.app_window.size(), (5, 4))
        self.worldManaged = weakref.WeakSet()
        self.worldHash = Fixed2DHash(WindowModule.app_window.size(), (5, 4))
        self.unmanaged = weakref.WeakSet()
        self.activeReciever = None

    def handle_event(self, event, wnd):
        pass

    def _reload(self, other):
        self.uiManaged = other.uiManaged
        self.uiHash = other.uiHash
        self.overlayManaged = other.overlayManaged
        self.overlayHash = other.overlayHash
        self.worldManaged = other.worldManaged
        self.worldHash = other.worldHash
        self.activeReciever = other.activeReciever


def handle_event(event, wnd):
    inputManager.handle_event(event, wnd)

def OnUIRecieverEnable(component, value):
    if value:
        component.input_stack_el = inputManager.uiManaged.push(component)
        component.input_hash_indx = inputManager.uiHash.register(component.rect)

@reloadable
class UIInputReciever(Component):
    def __init__(self):
        super(ManagedInputReciever._get_cls(), self).__init__(owner)
        self.OnEnable.append(OnUIRecieverEnable)
        self.OnEnable(self, True)

    def handle_event(self, event, wnd):
        return True