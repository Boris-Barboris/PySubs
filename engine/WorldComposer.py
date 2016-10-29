#   Copyright Alexander Baranin 2016

# World composer defines components, that are renderable in World layer
# We'll probably expand base classes here later
# TODO - add z-order

from engine.Reloadable import reloadable
from engine.GameObject import Component

from sfml.graphics import View
from sfml.graphics import Rectangle
from sfml.system import Vector2

import weakref

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('Composers', 'engine.SceneComposers'),
    ('WindowModule', 'engine.WindowModule'))

def onLoad(core):
    Logging.logMessage('WorldComposer is loading')
    global composer
    composer = WorldComposer._persistent('WorldComposer.composer')
    Composers.composers.WorldLayer = composer

def onUnload():
    Logging.logMessage('WorldComposer is unloading')


composer = None

@reloadable
class Camera:
    def __init__(self):
        self.position = Vector2(0, 0)
        # how many game units in 1 pixel:
        self.scale = 0.1

    def _reload(self, other):
        self.position = other.position
        self.scale = other.scale

@reloadable
class WorldComposer:
    def __init__(self):
        self.components = weakref.WeakSet()
        self.camera = Camera()
        self.view = View()

    def run(self):
        wnd = WindowModule.app_window
        wnd_size = wnd.size()
        # create view from camera and assign it to window
        self.view = self.get_view(self.camera, wnd_size)
        wnd.wnd_handle.view = self.view
        # iterale all worldRenderables
        for c in self.components:
            c.OnWorldRender(wnd, self.camera)

    def get_view(self, camera, wnd_size):
        return View(Rectangle(
            (self.camera.position.x - wnd_size.x * 0.5 * self.camera.scale,
             self.camera.position.y - wnd_size.y * 0.5 * self.camera.scale),
            (wnd_size.x * self.camera.scale, wnd_size.y * self.camera.scale)))

    def _reload(self, other):
        self.__init__()
        self.components = other.components
        self.camera = other.camera
        self.view = other.view

def onComponentEnable(obj, enabled):
    if enabled:
        composer.components.add(obj)
    else:
        try:
            composer.components.remove(obj)
        except KeyError:
            pass

@reloadable
class WorldRenderable(Component):
    def __init__(self, owner = None):
        super(WorldRenderable._get_cls(), self).__init__(owner)
        composer.components.add(self)
        self.OnEnable.append(onComponentEnable)

    def OnWorldRender(self, wnd, camera):
        pass
