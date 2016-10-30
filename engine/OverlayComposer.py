#   Copyright Alexander Baranin 2016

# Overlay composer defines components, that are renderable in overlay layer

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
    ('WindowModule', 'engine.WindowModule'),
    ('WorldComposer', 'engine.WorldComposer'))

def onLoad(core):
    Logging.logMessage('OverlayCmposer is loading')
    global composer
    composer = OverlayComposer._persistent('OverlayCmposer.composer')
    Composers.composers.OverlayLayer = composer

def onUnload():
    Logging.logMessage('OverlayCmposer is unloading')


composer = None

@reloadable
class OverlayComposer:
    def __init__(self, proxy):
        self.components = weakref.WeakSet()

    def run(self):
        wnd = WindowModule.app_window
        wnd_size = wnd.size()
        # create view from camera and assign it to window
        view = View(Rectangle((0, 0), (wnd_size.x, wnd_size.y)))
        wnd.wnd_handle.view = view
        camera = WorldComposer.composer.camera
        for c in self.components:
            c.OnOverlayRender(wnd, wnd_size, camera)

    def _reload(self, other, proxy):
        self.components = other.components

def onComponentEnable(obj, enabled):
    if enabled:
        composer.components.add(obj)
    else:
        try:
            composer.components.remove(obj)
        except KeyError:
            pass

@reloadable
class OverlayRenderable(Component):
    def __init__(self, proxy, owner = None):
        super(OverlayRenderable._get_cls(), self).__init__(proxy, owner)
        composer.components.add(proxy)
        self.OnEnable.append(onComponentEnable)

    def OnOverlayRender(self, wnd, wnd_size, camera):
        pass
