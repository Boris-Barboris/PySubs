#   Copyright Alexander Baranin 2016

import sfml

from sfml import window
from engine.Reloadable import reloadable

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'))

SCHED_ORDER = 10

def onLoad(core):
    Logging.logMessage('WindowModule is loading')
    global app_window
    app_window = Window._persistent('WindowModule.app_window')
    EngineCore.schedule_FIFO(run, SCHED_ORDER)

def onUnload():
    Logging.logMessage('WindowModule is unloading')
    global wnd_handle
    app_window.close_window()
    EngineCore.unschedule_FIFO(SCHED_ORDER)


app_window = None       # Main application window


@reloadable
class Window:
    '''Window abstraction in the engine'''
    background_color = (35, 35, 35)
    wnd_size = (800, 500)
    wnd_name = 'PySubs'
    vsync = True

    def __init__(self, name = wnd_name, 
                 size = wnd_size, 
                 clr = background_color):
        self.settings = window.ContextSettings(0, 0, 4, 2, 0)
        self.wnd_handle = sfml.RenderWindow(sfml.VideoMode(*size), 
            name, window.Style.RESIZE | window.Style.CLOSE, self.settings)
        self._fullscreen = False
        self.wnd_handle.vertical_synchronization = Window.vsync
        self.background_color = clr
        self.wnd_handle.clear(sfml.Color(*self.background_color))
        self.wnd_title = name
        self.wnd_size = size

    def close_window(self):
        self.wnd_handle.close()

    def set_window_title(self, title):
        self.wnd_handle.title = title
        self.wnd_title = title

    def is_fullscreen(self):
        return self._fullscreen

    def size(self):
        return self.wnd_handle.size

    def set_fullscreen(self, val):
        if val != self._fullscreen:
            if val:
                self.wnd_size = self.wnd_handle.size
                flscr_mode = sfml.VideoMode.get_fullscreen_modes()[0]
                self.wnd_handle.recreate(flscr_mode, self.wnd_title, 
                    window.Style.FULLSCREEN, self.settings)
            else:
                mode = sfml.VideoMode(*self.wnd_size)
                self.wnd_handle.recreate(mode, self.wnd_title, 
                    window.Style.RESIZE | window.Style.CLOSE, self.settings)
            self._fullscreen = val
            self.wnd_handle.vertical_synchronization = Window.vsync

    def draw(self, *args):
        self.wnd_handle.draw(*args)

    def display(self):
        self.wnd_handle.display()
        if not self._fullscreen:
            self.wnd_position = self.wnd_handle.position
        self.wnd_handle.clear(sfml.Color(*self.background_color))

    def _reload(self, other):
        self.__init__()
        self.set_fullscreen(other.is_fullscreen())
        # preserve window size
        self.wnd_size = other.wnd_size
        if not self._fullscreen:
            new_mode = sfml.VideoMode(*self.wnd_size)
            self.wnd_handle.recreate(new_mode, self.wnd_title, 
                window.Style.RESIZE | window.Style.CLOSE, self.settings)
            self.wnd_handle.position = other.wnd_position
        self.wnd_handle.vertical_synchronization = Window.vsync



def run():
    app_window.display()