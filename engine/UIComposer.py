#   Copyright Alexander Baranin 2016

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
    global composer
    composer = UIComposer._persistent('UIComposer.composer')
    Composers.composers.UILayer = composer

def onUnload():
    pass


composer = None

# TODO - add z-order

@reloadable
class UIComposer:
    def __init__(self, proxy):
        self.components = weakref.WeakSet()

    def run(self):
        wnd = WindowModule.app_window
        wnd_size = wnd.size()
        # create view from camera and assign it to window
        view = View(Rectangle((0, 0), (wnd_size.x, wnd_size.y)))
        wnd.wnd_handle.view = view
        # iterale all worldRenderables
        for c in self.components:
            c.OnUIRender(wnd)

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
class UIRenderable(Component):
    def __init__(self, proxy, owner = None):
        super(UIRenderable._get_cls(), self).__init__(proxy, owner)
        composer.components.add(proxy)
        self.OnEnable.append(onComponentEnable)

    def OnUIRender(self, wnd):
        pass
