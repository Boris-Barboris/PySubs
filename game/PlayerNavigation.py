#   Copyright Alexander Baranin 2016

import math
import sys

import sfml
from sfml.system import Vector2
from sfml.window import *

from engine.Reloadable import reloadable
from engine.mathutils import *

from engine.GameObject import *


_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('WorldComposer', 'engine.WorldComposer'),
    ('OverlayComposer', 'engine.OverlayComposer'),
    ('InputManager', 'engine.InputManager'),
    ('CameraController', 'game.CameraController'))

_subscribe_modules = [
    'engine.InputManager',
    'engine.OverlayComposer']

from engine.EngineCore import handle_imports

handle_imports(sys.modules[__name__])

def onLoad(core):
    global navigator
    navigator = PlayerNavigationInput._persistent('PlayerNavigation.navigator')
    InputManager.inputManager.unmanaged.add(navigator)

navigator = None

KEY_DIR_SPEED = 750
KEY_THROTTLE_SPEED = 2.0

HOTKEY_COURSE = Keyboard.W
HOTKEY_THROTTLE = Keyboard.S

COURSE = 1
THROTTLE = 2

@reloadable
class PlayerNavigationInput(InputManager.UnmanagedInputReciever, GameObject._get_cls()):
    def __init__(self, proxy):
        GameObject._get_cls().__init__(self, proxy)
        self.player_vessel = None
        self.mode = None
        self.desired_course = 0.0
        self.desired_throttle = 0.0
        self.dirlabel = DirectionLabel()
        self.addComponent(self.dirlabel, proxy)
        self.dirlabel.enabled = False
        self.throttlelabel = ThrottleLabel()
        self.addComponent(self.throttlelabel, proxy)
        self.throttlelabel.enabled = False
        self.mousepos_scr = Vector2(0, 0)

    def handle_mouse_event(self, event, wnd):
        if self.player_vessel is not None:
            if type(event) is MouseMoveEvent:
                self.mousepos_scr = event.position

    def change_desired_course(self):
        world_pos = WorldComposer.composer.screen_to_world(self.mousepos_scr)
        vec = world_pos - self.player_vessel.transform.lposition
        self.desired_course = rad2dgr(vecangle(vec)) + 90.0
        self.player_vessel.steersman.steer_course(self.desired_course)

    def stop_directing(self):
        self.mode = None
        self.dirlabel.enabled = False
        CameraController.controller.keys_captured = True
        self.change_desired_course()

    def stop_throttling(self):
        self.mode = None
        self.throttlelabel.enabled = False
        CameraController.controller.keys_captured = True
        if abs(self.desired_throttle) < 0.05:
            self.desired_throttle = 0.0
        if self.player_vessel is not None:
            self.player_vessel.ctrl_state.throttle = self.desired_throttle


    def handle_key_event(self, event, wnd):
        if event.code == HOTKEY_COURSE:
            if event.pressed and (self.mode is None):
                self.mode = COURSE
                self.dirlabel.enabled = True
                CameraController.controller.keys_captured = False
            if event.released:
                self.stop_directing()
        elif event.code == HOTKEY_THROTTLE:
            if event.pressed and (self.mode is None):
                self.mode = THROTTLE
                self.throttlelabel.enabled = True
                CameraController.controller.keys_captured = False
            if event.released:
                self.stop_throttling()

    def handle_frame(self, focused):
        if self.mode == COURSE and \
            not (Keyboard.is_key_pressed(HOTKEY_COURSE) and focused):
            self.stop_directing()
        if self.mode == COURSE:
            dt = min(EngineCore.frame_time, 0.1)
            camera = WorldComposer.composer.camera
            if Keyboard.is_key_pressed(Keyboard.RIGHT):
                self.mousepos_scr += Vector2(KEY_DIR_SPEED, 0.0) * dt
            if Keyboard.is_key_pressed(Keyboard.UP):
                self.mousepos_scr += Vector2(0.0, -KEY_DIR_SPEED) * dt
            if Keyboard.is_key_pressed(Keyboard.LEFT):
                self.mousepos_scr += Vector2(-KEY_DIR_SPEED, 0.0) * dt
            if Keyboard.is_key_pressed(Keyboard.DOWN):
                self.mousepos_scr += Vector2(0.0, KEY_DIR_SPEED) * dt
        elif self.mode == THROTTLE:
            dt = min(EngineCore.frame_time, 0.1)
            if Keyboard.is_key_pressed(Keyboard.UP):
                self.desired_throttle += KEY_THROTTLE_SPEED * dt
            if Keyboard.is_key_pressed(Keyboard.DOWN):
                self.desired_throttle -= KEY_THROTTLE_SPEED * dt
            self.desired_throttle = clmp1(self.desired_throttle)
            self.throttlelabel.set_pointer(self.desired_throttle)

        if self.player_vessel is not None:
            self.player_vessel.steersman.steer_course(self.desired_course)
            self.vesselpos_scr = WorldComposer.composer.world_to_screen(
                self.player_vessel.transform.lposition)



    def _reload(self, other, proxy):
        GameObject._reload(self, other, proxy)
        self.player_vessel = other.player_vessel
        self.mode = None
        self.desired_course = other.desired_course
        self.desired_throttle = getattr(other, 'desired_throttle', 0.0)
        self.dirlabel = other.dirlabel
        self.dirlabel.enabled = False
        self.throttlelabel = other.throttlelabel
        self.throttlelabel.enabled = False
        self.mousepos_scr = other.mousepos_scr


@reloadable
class DirectionLabel(OverlayComposer.OverlayRenderable):
    def __init__(self, proxy):
        super(DirectionLabel._get_cls(), self).__init__(proxy)
        self.init_label()

    def init_label(self):
        self.label = RectangleShape()
        self.label.fill_color = Color(255, 255, 0, 50)
        self.label.position = (-1.0, -1.0)
        self.label.size = (2.0, 1.0)
        self.label.outline_thickness = 0.0

    def OnOverlayRender(self, wnd, wnd_size, camera):
        if self.owner.player_vessel is not None:
            vec = self.owner.mousepos_scr - self.owner.vesselpos_scr
            angle = rad2dgr(vecangle(vec)) + 90.0
            self.label.position = self.owner.vesselpos_scr
            self.label.rotation = angle
            self.label.ratio = (1.0, -vec_len(vec))
            wnd.draw(self.label)

    def _reload(self, other, proxy):
        super(DirectionLabel._get_cls(), self)._reload(other, proxy)
        self.init_label()


@reloadable
class ThrottleLabel(OverlayComposer.OverlayRenderable):
    def __init__(self, proxy):
        super(ThrottleLabel._get_cls(), self).__init__(proxy)
        self.init_label()

    def init_label(self):
        self.frame = RectangleShape()
        self.frame.fill_color = Color.TRANSPARENT
        self.frame.position = (10, 100)
        self.frame.size = (15, 200)
        self.frame.outline_thickness = 1.0
        self.frame.outline_color = Color.WHITE

        self.pointer = RectangleShape()
        self.pointer.fill_color = Color(255, 255, 255, 100)
        self.pointer.position = (10, 200)
        self.pointer.size = (15, 100)
        self.pointer.outline_thickness = 0.0

    def set_pointer(self, throttle):
        self.pointer.ratio = (1.0, -throttle)

    def OnOverlayRender(self, wnd, wnd_size, camera):
        wnd.draw(self.pointer)
        wnd.draw(self.frame)

    def _reload(self, other, proxy):
        super(ThrottleLabel._get_cls(), self)._reload(other, proxy)
        self.init_label()
