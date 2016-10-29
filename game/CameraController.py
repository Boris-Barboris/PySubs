#   Copyright Alexander Baranin 2016

import sfml
from sfml.system import Vector2
import math


_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('WorldComposer', 'engine.WorldComposer'),
    ('IOBroker', 'engine.IOBroker'))

def onLoad(core):
    Logging.logMessage('CameraController is loading')
    IOBroker.register_handler(handle_zoom, sfml.window.MouseWheelEvent)
    IOBroker.register_handler(handle_click, sfml.window.MouseButtonEvent)
    IOBroker.register_handler(handle_move, sfml.window.MouseMoveEvent)

def onUnload():
    Logging.logMessage('CameraController is unloading')
    IOBroker.unregister_handler(handle_zoom, sfml.window.MouseWheelEvent)
    IOBroker.unregister_handler(handle_click, sfml.window.MouseButtonEvent)
    IOBroker.unregister_handler(handle_move, sfml.window.MouseMoveEvent)

def handle_zoom(event, wnd):
    delta = event.delta
    camera = WorldComposer.composer.camera
    scale_shift = delta * 0.01 * (1.0 + camera.scale * 10.0)
    camera.scale -= scale_shift
    camera.scale = max(0.05, camera.scale)
    camera.scale = min(10.0, camera.scale)
    if delta > 0 and positional_zoom and camera.scale > 0.05:
        pos = event.position
        size = wnd.size()
        shift = (pos - size * 0.5) * scale_shift
        camera.position += shift

panning = False
positional_zoom = False

def handle_click(event, wnd):
    global panning
    if event.button == sfml.window.Mouse.RIGHT:
        if event.pressed:
            panning = True
            global prev_pos
            prev_pos = event.position
        if event.released:
            panning = False

prev_pos = None

def handle_move(event, wnd):
    global prev_pos
    if panning:
        if prev_pos is None:
            prev_pos = event.position
            return
        delta = event.position - prev_pos
        camera = WorldComposer.composer.camera
        camera.position -= delta * camera.scale
        prev_pos = event.position
