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

KEY_DIR_SPEED = 500

HOTKEY_COURSE = Keyboard.W

@reloadable
class PlayerNavigationInput(InputManager.UnmanagedInputReciever, GameObject._get_cls()):
    def __init__(self, proxy):
        GameObject._get_cls().__init__(self, proxy)
        self.player_vessel = None
        self.directing = False
        self.desired_course = 0.0
        self.dirlabel = DirectionLabel()
        self.addComponent(self.dirlabel, proxy)
        self.dirlabel.enabled = False
        self.mousepos_scr = Vector2(0, 0)

    def handle_mouse_event(self, event, wnd):
        if self.player_vessel is not None:
            if type(event) is MouseButtonEvent:
                if self.directing and event.button == Mouse.LEFT and event.pressed:
                    self.mousepos_scr = event.position
                    self.stop_directing()
            if type(event) is MouseMoveEvent:
                self.mousepos_scr = event.position

    def change_desired_course(self):
        world_pos = WorldComposer.composer.screen_to_world(self.mousepos_scr)
        vec = world_pos - self.player_vessel.transform.lposition
        self.desired_course = rad2dgr(vecangle(vec)) + 90.0
        self.player_vessel.steersman.steer_course(self.desired_course)

    def stop_directing(self):
        self.directing = False
        self.dirlabel.enabled = False
        CameraController.controller.keys_captured = True
        self.change_desired_course()

    def handle_key_event(self, event, wnd):
        if event.code == HOTKEY_COURSE:
            if event.pressed:
                self.directing = True
                self.dirlabel.enabled = True
                CameraController.controller.keys_captured = False
            if event.released:
                self.stop_directing()

    def handle_frame(self, focused):
        if self.player_vessel is not None:
            self.player_vessel.steersman.steer_course(self.desired_course)
            self.vesselpos_scr = WorldComposer.composer.world_to_screen(
                self.player_vessel.transform.lposition)
        if self.directing and (not Keyboard.is_key_pressed(HOTKEY_COURSE) or \
            not focused):
            self.stop_directing()
        if self.directing:
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


    def _reload(self, other, proxy):
        GameObject._reload(self, other, proxy)
        self.player_vessel = other.player_vessel
        self.directing = False
        self.desired_course = other.desired_course
        self.dirlabel = other.dirlabel
        self.dirlabel.enabled = False
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