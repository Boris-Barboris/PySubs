#   Copyright Alexander Baranin 2016

import math
import sys

import sfml
from sfml.system import Vector2
from sfml.window import Keyboard

from engine.Reloadable import reloadable


_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('WorldComposer', 'engine.WorldComposer'),
    ('InputManager', 'engine.InputManager'))

_subscribe_modules = [
    'engine.InputManager']

from engine.EngineCore import handle_imports

handle_imports(sys.modules[__name__])

def onLoad(core):
    Logging.logMessage('CameraController is loading')
    global controller
    controller = CameraController._persistent('CameraController.controller')
    InputManager.inputManager.unmanaged.add(controller)

def onUnload():
    Logging.logMessage('CameraController is unloading')

controller = None

POSITIONAL_ZOOM = True
KEY_PAN_SPEED = 1000.0

@reloadable
class CameraController(InputManager.UnmanagedInputReciever):
    def __init__(self, proxy):
        self.panning = False
        self.prev_pos = None

    def handle_mouse_event(self, event, wnd):
        if type(event) is sfml.window.MouseWheelEvent:
            self.handle_zoom(event, wnd)
        elif type(event) is sfml.window.MouseButtonEvent:
            self.handle_click(event, wnd)
        elif type(event) is sfml.window.MouseMoveEvent:
            self.handle_move(event, wnd)

    def handle_frame(self):
        self.handle_key()

    def handle_zoom(self, event, wnd):
        delta = event.delta * 0.01
        camera = WorldComposer.composer.camera
        scale_shift = self.do_zoom(camera, delta)
        if delta > 0 and POSITIONAL_ZOOM and camera.scale > 0.05:
            pos = event.position
            size = wnd.size()
            shift = (pos - size * 0.5) * scale_shift * 0.75
            camera.position += shift
            
    def do_zoom(self, camera, zoom_delta):
        scale_shift = zoom_delta * (1.0 + camera.scale * 10.0)
        camera.scale -= scale_shift
        camera.scale = max(0.05, camera.scale)
        camera.scale = min(10.0, camera.scale)
        return scale_shift

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

    def handle_key(self):
        dt = min(EngineCore.frame_time, 0.1)
        camera = WorldComposer.composer.camera
        if Keyboard.is_key_pressed(Keyboard.RIGHT):
            camera.position += Vector2(KEY_PAN_SPEED, 0.0) * camera.scale * dt
        if Keyboard.is_key_pressed(Keyboard.UP):
            camera.position += Vector2(0.0, -KEY_PAN_SPEED) * camera.scale * dt
        if Keyboard.is_key_pressed(Keyboard.LEFT):
            camera.position += Vector2(-KEY_PAN_SPEED, 0.0) * camera.scale * dt
        if Keyboard.is_key_pressed(Keyboard.DOWN):
            camera.position += Vector2(0.0, KEY_PAN_SPEED) * camera.scale * dt
        if Keyboard.is_key_pressed(Keyboard.ADD) or \
           Keyboard.is_key_pressed(Keyboard.E):
            self.do_zoom(camera, dt * 0.15)
        if Keyboard.is_key_pressed(Keyboard.SUBTRACT) or \
           Keyboard.is_key_pressed(Keyboard.Q):
            self.do_zoom(camera, -dt * 0.15)
