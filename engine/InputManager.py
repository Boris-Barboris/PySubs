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
#
# Mouse events can change active reciever. Keyboard and joystick ones can not.
# All recievers are assumed to have rectangular form - used for hashing.
# Actual, precise check is done via checkPoint function.
# 
# Reciever right under the mouse is called 'cursored', there are events to
# handle that like OnMouseEnter and OnMouseLeave
#
# Possibly, in the future World overlay will migrate to physics Module.

import sfml
from sfml.graphics import Rectangle
from sfml.system import Vector2

from engine.Event import Event

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
    IOBroker.register_handler(handle_mouse_event, sfml.window.MouseMoveEvent)
    IOBroker.register_handler(handle_mouse_event, sfml.window.MouseWheelEvent)
    IOBroker.register_handler(handle_mouse_event, sfml.window.MouseButtonEvent)
    IOBroker.register_handler(handle_mouse_event, sfml.window.MouseEvent)

def onUnload():
    Logging.logMessage('InputManager is unloading')
    IOBroker.unregister_handler(handle_mouse_event, sfml.window.MouseMoveEvent)
    IOBroker.unregister_handler(handle_mouse_event, sfml.window.MouseWheelEvent)
    IOBroker.unregister_handler(handle_mouse_event, sfml.window.MouseButtonEvent)
    IOBroker.unregister_handler(handle_mouse_event, sfml.window.MouseEvent)


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
        self.cursored = None

    def handle_mouse_event(self, event, wnd):
        if type(event) is sfml.window.MouseEvent:
            if event.left:
                if self.cursored is not None:
                    self.cursored.OnMouseLeave()
            return

        point = event.position
        # UI layer
        reciever = None
        candidates = self.uiHash.cell(point)
        if candidates is not None:
            sorted_cand = sorted(candidates, 
                key = lambda x: x.input_stack_el.index)
            reciever = next((x for x in sorted_cand if x.checkPoint(point)), None)
            if reciever is not None:
                self.activeReciever = reciever
                if self.cursored is not reciever:
                    if self.cursored is not None:
                        self.cursored.OnMouseLeave()
                    reciever.OnMouseEnter()
                    self.cursored = reciever
                if not reciever.handle_event(event, wnd):
                    return
            else:
                self.activeReciever = False
                if self.cursored is not None:
                    self.cursored.OnMouseLeave()
                self.cursored = None            
        # Overlay layer
        candidates = self.overlayHash.cell(point)
        if candidates is not None:
            sorted_cand = sorted(candidates, 
                key = lambda x: x.input_stack_el.index)
            reciever = next((x for x in sorted_cand if x.checkPoint(point)), None)
            if reciever is not None:
                if not reciever.handle_event(event, wnd):
                    return
        # World layer
        candidates = self.worldHash.cell(point)
        if candidates is not None:
            sorted_cand = sorted(candidates, 
                key = lambda x: x.input_stack_el.index)
            reciever = next((x for x in sorted_cand if x.checkPoint(point)), None)
            if reciever is not None:
                if not reciever.handle_event(event, wnd):
                    return

        if reciever is None:
            if self.cursored is not None:
                self.cursored.OnMouseLeave()
            self.cursored = None
        # Unmanaged recievers
        for reciever in self.unmanaged:
            reciever.handle_event(event, wnd)

    def _reload(self, other):
        self.uiManaged = other.uiManaged
        self.uiHash = other.uiHash
        self.overlayManaged = other.overlayManaged
        self.overlayHash = other.overlayHash
        self.worldManaged = other.worldManaged
        self.worldHash = other.worldHash
        self.activeReciever = other.activeReciever
        self.unmanaged = other.unmanaged
        self.cursored = other.cursored


def handle_mouse_event(event, wnd):
    inputManager.handle_mouse_event(event, wnd)

def OnUIRecieverEnable(component, value):
    if value:
        component.input_stack_el = inputManager.uiManaged.push(component)
        component.input_hash_indx = inputManager.uiHash.register(
                                        component.rect, component)
    else:
        inputManager.uiManaged.removeElem(component.input_stack_el)
        inputManager.uiHash.unregister(component, component.input_hash_indx)

def OnUIRecieverRectUpdate(reciever):
    inputManager.uiHash.unregister(reciever, reciever.input_hash_indx)
    reciever.input_hash_indx = inputManager.uiHash.register(
                                        reciever.rect, reciever)


@reloadable
class UIInputReciever(Component):
    def __init__(self, rect):
        super(UIInputReciever._get_cls(), self).__init__()
        self.rect = rect
        self.OnEnable.append(OnUIRecieverEnable)
        self.OnEnable(self, True)
        self.OnRectangleChange = Event()
        self.OnRectangleChange.append(OnUIRecieverRectUpdate)
        self.OnMouseEnter = Event()
        self.OnMouseLeave = Event()

    def handle_event(self, event, wnd):
        if type(event) is sfml.window.MouseButtonEvent:
            self.input_stack_el.moveToHead()
            return False
        return True

    def checkPoint(self, point):
        return self.rect.contains(point)

    def _reload(self, other):
        self.rect = other.rect
        self.OnEnable = other.OnEnable
        self.OnRectangleChange = other.OnRectangleChange
        self.input_stack_el = other.input_stack_el
        self.input_hash_indx = other.input_hash_indx
        self.OnMouseEnter = other.OnMouseEnter
        self.OnMouseLeave = other.OnMouseLeave