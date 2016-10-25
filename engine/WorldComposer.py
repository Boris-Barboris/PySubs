#   Copyright Alexander Baranin 2016

# World composer defines components, that are renderable in World layer
# We'll probably expand base classes here later

from engine.Reloadable import reloadable
from engine.GameObject import Component

from sfml.graphics import View
from sfml.graphics import Rectangle

import weakref

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('Composers', 'engine.SceneComposers'),
    ('WindowModule', 'engine.WindowModule'))

def onLoad(core):
    Logging.logMessage('WorldComposer is loading')
    global composer
    camera = Camera()
    composer = WorldComposer._persistent('WorldComposer.composer')
    Composers.composers.WorldLayer = composer

def onUnload(core):
    Logging.logMessage('WorldComposer is unloading')


composer = None

@reloadable
class Camera:
    def __init__(self):
        self.position = (0.0, 0.0)
        # how many game units in 1 pixel:
        self.scale = 0.4

    def _reload(self, other):
        self.position = other.position
        self.scale = other.scale

@reloadable
class WorldComposer:
    def __init__(self):
        self.components = weakref.WeakSet()
        self.camera = Camera()

    def run(self):
        wnd = WindowModule.app_window
        wnd_size = wnd.size()
        # create view from camera and assign it to window
        view = View(Rectangle(
            (self.camera.position[0] - wnd_size.x * 0.5 * self.camera.scale,
             self.camera.position[1] - wnd_size.y * 0.5 * self.camera.scale),
            (wnd_size.x * self.camera.scale, wnd_size.y * self.camera.scale)))
        wnd.wnd_handle.view = view
        # iterale all worldRenderables
        for c in self.components:
            if c.active():
                c.OnWorldRender(wnd)

    def _reload(self, other):
        self.components = other.components

@reloadable
class WorldRenderable(Component):
    def __init_rld__(self, proxy, owner = None):
        super(WorldRenderable._get_cls(), self).__init__(owner)
        composer.components.add(proxy)

    def OnWorldRender(self, wnd):
        pass
