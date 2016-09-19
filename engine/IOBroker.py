#   Copyright Alexander Baranin 2016

import sfml

from engine.Reloadable import reloadable, freeze_module_instances, \
    reload_module_instances, unfreeze_module_instances

Logging = None
EngineCore = None
WindowModule = None

SCHED_ORDER = 20

def onLoad(core):
    global EngineCore
    EngineCore = core
    global Logging
    Logging = EngineCore.loaded_modules['engine.Logging']
    global WindowModule
    WindowModule = EngineCore.loaded_modules['engine.WindowModule']
    Logging.logMessage('IOBroker is loading')
    EngineCore.schedule_FIFO(run, SCHED_ORDER)
    # load event map
    reload_module_instances(__name__)
    global event_map    
    event_map = EventHandlerMap._persistent('IOBroker.event_map')
    unfreeze_module_instances(__name__)
    # standard window event handlers
    register_handler(close_std_event, sfml.window.CloseEvent)
    register_handler(fullscreen_std_event, sfml.window.KeyEvent)
    register_handler(resize_std_event, sfml.window.ResizeEvent)

def onUnload():
    Logging.logMessage('IOBroker is unloading')
    # standard window event handlers
    freeze_module_instances(__name__)
    unregister_handler(close_std_event, sfml.window.CloseEvent)
    unregister_handler(fullscreen_std_event, sfml.window.KeyEvent)
    unregister_handler(resize_std_event, sfml.window.ResizeEvent)
    EngineCore.unschedule_FIFO(SCHED_ORDER)   
    
     

event_map = None        # static reloadable event map


@reloadable
class EventHandlerMap:
    def __init__(self):
        self._handlers = {}

    def _reload(self, other):
        for event in other._handlers:
            if event in self._handlers:
                self._handlers[event].extend(other._handlers[event])
            else:
                self._handlers[event] = other._handlers[event]

    def register_handler(self, f, event_type):
        if event_type in self._handlers:
            self._handlers[event_type].append(f)
        else:
            self._handlers[event_type] = [f]

    def unregister_handler(self, f, event_type):
        if event_type in self._handlers:
            if f in self._handlers[event_type]:
                self._handlers[event_type].remove(f)
                if len(self._handlers[event_type]) == 0:
                    del self._handlers[event_type]


def run():
    for event in WindowModule.app_window.wnd_handle.events:
        t = type(event)
        d = event_map._handlers
        if t in d:
            handlers_list = d[t]
            for hdlr in handlers_list:
                hdlr(event, WindowModule.app_window)

def register_handler(f, event_type):
    event_map.register_handler(f, event_type)

def unregister_handler(f, event_type):
    event_map.unregister_handler(f, event_type)

# Standard handlers themselves

def close_std_event(event, wnd):
    # close window
    wnd.close_window()
    EngineCore.request_shutdown()

def fullscreen_std_event(event, wnd):
    # switch fullscreen on\off
    if event.code == sfml.window.Keyboard.F and event.pressed:
        wnd.set_fullscreen(not wnd.is_fullscreen())

def resize_std_event(event, wnd):
    # window was resized
    if not wnd.is_fullscreen():
        wnd.wnd_size = event.size