#   Copyright Alexander Baranin 2016

import sfml
from sfml.system import Vector2
from engine.Reloadable import reloadable
import math


_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('WorldComposer', 'engine.WorldComposer'),
    ('InputManager', 'engine.InputManager'))

def onLoad(core):
    Logging.logMessage('CameraController is loading')
    global controller
    controller = CameraController._persistent('CameraController.controller')
    InputManager.inputManager.unmanaged.add(controller)

def onUnload():
    Logging.logMessage('CameraController is unloading')

controller = None

POSITIONAL_ZOOM = True

@reloadable
class CameraController:
    def __init__(self):
        self.panning = False
        self.prev_pos = None

    def handle_event(self, event, wnd):
        if type(event) is sfml.window.MouseWheelEvent:
            self.handle_zoom(event, wnd)
        elif type(event) is sfml.window.MouseButtonEvent:
            self.handle_click(event, wnd)
        elif type(event) is sfml.window.MouseMoveEvent:
            self.handle_move(event, wnd)

    def handle_zoom(self, event, wnd):
        delta = event.delta
        camera = WorldComposer.composer.camera
        scale_shift = delta * 0.01 * (1.0 + camera.scale * 10.0)
        camera.scale -= scale_shift
        camera.scale = max(0.05, camera.scale)
        camera.scale = min(10.0, camera.scale)
        if delta > 0 and POSITIONAL_ZOOM and camera.scale > 0.05:
            pos = event.position
            size = wnd.size()
            shift = (pos - size * 0.5) * scale_shift * 0.5
            camera.position += shift

    def handle_click(self, event, wnd):
        if event.button == sfml.window.Mouse.RIGHT:
            if event.pressed:
                self.panning = True
                self.prev_pos = event.position
            if event.released:
                self.panning = False

    def handle_move(self, event, wnd):
        if self.panning:
            if self.prev_pos is None:
                self.prev_pos = event.position
                return
            delta = event.position - self.prev_pos
            camera = WorldComposer.composer.camera
            camera.position -= delta * camera.scale
            self.prev_pos = event.position
