#   Copyright Alexander Baranin 2016

# Here we introduce the concept of input focus. All input events are
# first routed to active input reciever, wich performs some actions according
# to it's logic and then returns True if it lets the event to go through to
# global(unmanaged) event handlers. Those are non-exclusive and handle all events 
# that are left. State in which no active reciever is perfectly valid.
#
# Typical managed event consumer is some UI primitive (Button, window, label,
#   game object collision box...), wich leads us to the concept of z-order.
# Al managed recievers will be split onto 3 ordered layers (World, Overlay, UI).
# World layer components will manage depth on their own (sice they usually tend
# to have their own concept of depth) via world_depth(). 
# Other two are ordered by InputManager.
#
# Mouse events can change active reciever. Keyboard and joystick ones can not.
# All recievers are assumed to have rectangular form - used for hashing.
# Actual, precise check is done via checkPoint function.
# 
# Reciever right under the mouse is called 'cursored', there are events to
# handle that like OnMouseEnter and OnMouseLeave. 
#
# Possibly, in the future World overlay will migrate to physics Module.

import sfml
from sfml.graphics import Rectangle
from sfml.system import Vector2
import time

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

SCHED_ORDER = 35    # some unmanaged recieves want to handle input every frame

def onLoad(core):
    Logging.logMessage('InputManager is loading')
    global inputManager
    inputManager = InputManager._persistent('InputManager.inputManager')
    IOBroker.register_handler(handle_mouse_event, sfml.window.MouseMoveEvent)
    IOBroker.register_handler(handle_mouse_event, sfml.window.MouseWheelEvent)
    IOBroker.register_handler(handle_mouse_event, sfml.window.MouseButtonEvent)
    IOBroker.register_handler(handle_mouse_event, sfml.window.MouseEvent)
    IOBroker.register_handler(handle_keyboard_event, sfml.window.KeyEvent)
    IOBroker.register_handler(handle_focus_event, sfml.window.FocusEvent)
    EngineCore.schedule_FIFO(run, SCHED_ORDER)

def onUnload():
    Logging.logMessage('InputManager is unloading')
    IOBroker.unregister_handler(handle_mouse_event, sfml.window.MouseMoveEvent)
    IOBroker.unregister_handler(handle_mouse_event, sfml.window.MouseWheelEvent)
    IOBroker.unregister_handler(handle_mouse_event, sfml.window.MouseButtonEvent)
    IOBroker.unregister_handler(handle_mouse_event, sfml.window.MouseEvent)
    IOBroker.unregister_handler(handle_keyboard_event, sfml.window.KeyEvent)
    IOBroker.unregister_handler(handle_focus_event, sfml.window.FocusEvent)
    EngineCore.unschedule_FIFO(SCHED_ORDER)


inputManager = None

@reloadable
class InputManager:
    def __init__(self, proxy):
        self.uiManaged = WeakOrderedDeque()
        self.uiHash = Fixed2DHash(WindowModule.app_window.size(), (5, 4))
        self.overlayManaged = WeakOrderedDeque()
        self.overlayHash = Fixed2DHash(WindowModule.app_window.size(), (5, 4))
        self.worldManaged = weakref.WeakSet()
        self.worldHash = Fixed2DHash(WindowModule.app_window.size(), (5, 4))
        self.unmanaged = weakref.WeakSet()
        self.activeReciever = None
        self.cursored = None
        self.focused = True

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
                key = lambda x: x.stack_el.index)
            reciever = next((x for x in sorted_cand if x.checkPoint(point)), None)
            if reciever is not None:
                self.activeReciever = reciever
                if self.cursored is not reciever:
                    self.clear_cursored()
                    reciever.OnMouseEnter()
                    self.cursored = reciever
                if not reciever.handle_mouse_event(event, wnd):
                    return
            else:
                self.activeReciever = None
                         
        # Overlay layer
        candidates = self.overlayHash.cell(point)
        if candidates is not None:
            sorted_cand = sorted(candidates, 
                key = lambda x: x.stack_el.index)
            reciever = next((x for x in sorted_cand if x.checkPoint(point)), None)
            if reciever is not None:
                if not reciever.handle_mouse_event(event, wnd):
                    return
        # World layer
        candidates = self.worldHash.cell(point)
        if candidates is not None:
            sorted_cand = sorted(candidates, 
                key = lambda x: x.world_depth())
            reciever = next((x for x in sorted_cand if x.checkPoint(point)), None)
            if reciever is not None:
                if not reciever.handle_mouse_event(event, wnd):
                    return

        if reciever is None:
            self.clear_cursored()
        # Unmanaged recievers
        for reciever in self.unmanaged:
            reciever.handle_mouse_event(event, wnd)

    def handle_focus_event(self, event, wnd):
        if event.lost:
            self.focused = False
            self.clear_cursored()
        elif event.gained:
            self.focused = True

    def handle_keyboard_event(self, event, wnd):
        if self.activeReciever is not None:
            res = self.activeReciever.handle_key_event(event, wnd)
            if not res:
                return
        for reciever in self.unmanaged:
            reciever.handle_key_event(event, wnd)

    def handle_frame(self):
        for reciever in self.unmanaged:
            reciever.handle_frame(self.focused)

    def clear_cursored(self):
        if self.cursored is not None:
            self.cursored.OnMouseLeave()
        self.cursored = None   

    def _reload(self, other, proxy):
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

def handle_keyboard_event(event, wnd):
    inputManager.handle_keyboard_event(event, wnd)

def handle_focus_event(event, wnd):
    inputManager.handle_focus_event(event, wnd)

def run():
    inputManager.handle_frame()

def OnUIRecieverEnable(component, value):
    if value:
        component.stack_el = inputManager.uiManaged.push(component)
        component.hash_index = inputManager.uiHash.register(
                                        component.rect, component)
    else:
        inputManager.uiManaged.removeElem(component.stack_el)
        inputManager.uiHash.unregister(component, component.hash_index)

def OnUIRecieverRectUpdate(reciever):
    inputManager.uiHash.unregister(reciever, reciever.hash_index)
    reciever.hash_index = inputManager.uiHash.register(
                                        reciever.rect, reciever)


@reloadable
class UIInputReciever(Component):
    def __init__(self, proxy, rect):
        super(UIInputReciever._get_cls(), self).__init__(proxy)
        self.rect = rect
        self.OnEnable.append(OnUIRecieverEnable)
        self.OnEnable(proxy, True)
        self.OnRectangleChange = Event()
        self.OnRectangleChange.append(OnUIRecieverRectUpdate)
        self.OnMouseEnter = Event()
        self.OnMouseLeave = Event()

    def handle_mouse_event(self, event, wnd):
        if type(event) is sfml.window.MouseButtonEvent:
            self.input_stack_el.moveToHead()
        return False

    def handle_key_event(self, event, wnd):
        return True

    def checkPoint(self, point):
        return self.rect.contains(point)

    def _reload(self, other, proxy):
        super(UIInputReciever._get_cls(), self)._reload(other, proxy)
        self.rect = other.rect
        self.OnRectangleChange = other.OnRectangleChange
        self.stack_el = other.stack_el
        self.hash_index = other.hash_index
        self.OnMouseEnter = other.OnMouseEnter
        self.OnMouseLeave = other.OnMouseLeave

@reloadable
class UnmanagedInputReciever:
    def handle_mouse_event(self, event, wnd):
        pass

    def handle_key_event(self, event, wnd):
        pass

    def handle_frame(self):
        pass