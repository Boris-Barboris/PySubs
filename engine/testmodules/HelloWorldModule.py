#   Copyright Alexander Baranin 2016

import sfml
import time
import math

from sfml.graphics import Text
from sfml.graphics import View
from sfml.graphics import Rectangle
from sfml.graphics import ConvexShape
from sfml.graphics import Color
from sfml.system import Vector2


import engine.TextManager as TextManager
import engine.EngineCore as EngineCore
import engine.Logging as Logging
import engine.WindowModule as WindowModule


SCHED_ORDER = 40

def onLoad(core):
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

    global triangle
    triangle = ConvexShape()
    triangle.texture = None
    triangle.fill_color = Color(150, 150, 255, 60)
    triangle.outline_color = Color(255, 255, 255, 255)
    triangle.outline_thickness = 2.0
    triangle.point_count = 3
    triangle.set_point(0, (0, -20))
    triangle.set_point(1, (20.0 * math.cos(math.radians(30)), 
                           20.0 * math.sin(math.radians(30))))
    triangle.set_point(2, (-20.0 * math.cos(math.radians(30)), 
                           20.0 * math.sin(math.radians(30))))

    EngineCore.schedule_FIFO(run, SCHED_ORDER)


def onUnload():
    Logging.logMessage('HelloWorldModule is unloading')
    EngineCore.unschedule_FIFO(SCHED_ORDER)

# texts
center_text = None
fps_text = None
clr = sfml.graphics.Color(255, 255, 255)
style = Text.REGULAR
view = None

# FPS
avg_fps = 60.0
time_hp = time.clock()

# Triangle
triangle = None

def run():
    wnd = WindowModule.app_window
    wnd_size = wnd.wnd_handle.size
        
    view.reset(Rectangle((0, 0), wnd_size))
    wnd.wnd_handle.view = view

    textbounds = center_text.local_bounds
    x = int(wnd_size[0] / 2.0 - (textbounds.width + textbounds.left) / 2.0)
    y = int(wnd_size[1] * 0.66 - (textbounds.height + textbounds.top) / 2.0)
    center_text.position = (x, y)
    wnd.draw(center_text)

    # FPS counter
    global time_hp, avg_fps
    frame_time = time.clock() - time_hp
    time_hp += frame_time
    avg_fps = 0.8 * avg_fps + 0.2 / frame_time

    fps_text.string = "{0:.1f}".format(avg_fps)
    textbounds = fps_text.local_bounds
    x = int(wnd_size[0] - (textbounds.width + textbounds.left) - 5)
    y = int(0 - textbounds.top + 5)
    fps_text.position = (x, y)
    wnd.draw(fps_text)

    # triangle
    triangle.position = Vector2(wnd_size[0] / 2.0, wnd_size[1] / 3)
    scale_factor = wnd_size[1] / 100.0
    triangle.ratio = Vector2(scale_factor, scale_factor)
    triangle.rotate(60 * frame_time)
    wnd.draw(triangle)
