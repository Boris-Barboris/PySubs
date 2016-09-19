#   Copyright Alexander Baranin 2016

import sfml
import time

from sfml.graphics import Text
from sfml.graphics import View
from sfml.graphics import Rectangle

Logging = None
EngineCore = None
WindowModule = None
TextManager = None

SCHED_ORDER = 40

def onLoad(core):
    global EngineCore
    EngineCore = core
    global Logging
    Logging = EngineCore.loaded_modules['engine.Logging']
    global WindowModule
    WindowModule = EngineCore.loaded_modules['engine.WindowModule']
    global TextManager
    TextManager = EngineCore.loaded_modules['engine.TextManager']

    Logging.logMessage('HelloWorldModule is loading')
    
    fnt = TextManager.load_font('calibri.ttf')
    global center_text    
    center_text = Text('Boobs Engine', fnt, 40)
    center_text.color = clr
    center_text.style = style
    global fps_text    
    fps_text = Text('60', fnt, 20)
    fps_text.color = clr
    fps_text.style = style
    global view
    view = View(Rectangle((0, 0), WindowModule.app_window.wnd_handle.size))
    EngineCore.schedule_FIFO(run, SCHED_ORDER)


def onUnload():
    Logging.logMessage('HelloWorldModule is unloading')
    EngineCore.unschedule_FIFO(SCHED_ORDER)

center_text = None
fps_text = None
clr = sfml.graphics.Color(255, 255, 255)
style = Text.REGULAR
view = None

avg_fps = 60.0
time_hp = time.clock()

def run():
    wnd = WindowModule.app_window
    wnd_size = wnd.wnd_handle.size

    view.reset(Rectangle((0, 0), wnd_size))
    wnd.wnd_handle.view = view

    textbounds = center_text.local_bounds
    x = int(wnd_size[0] / 2.0 - (textbounds.width + textbounds.left) / 2.0)
    y = int(wnd_size[1] / 2.0 - (textbounds.height + textbounds.top) / 2.0)
    center_text.position = (x, y)
    wnd.draw(center_text)

    # FPS counter
    global time_hp, avg_fps
    frame_time = time.clock() - time_hp
    time_hp += frame_time
    avg_fps = 0.5 * avg_fps + 0.5 / frame_time

    fps_text.string = "{0:.1f}".format(avg_fps)
    textbounds = fps_text.local_bounds
    x = int(wnd_size[0] - (textbounds.width + textbounds.left) - 5)
    y = int(0 - textbounds.top + 5)
    fps_text.position = (x, y)
    wnd.draw(fps_text)
