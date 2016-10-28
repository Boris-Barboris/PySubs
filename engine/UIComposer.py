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
    Logging.logMessage('UIComposer is loading')
    global composer
    composer = WorldComposer._persistent('UIComposer.composer')
    Composers.composers.UILayer = composer

def onUnload():
    Logging.logMessage('UIComposer is unloading')


composer = None


@reloadable
class UIComposer:
    def __init__(self):
        self.components = weakref.WeakSet()

    def run(self):
        wnd = WindowModule.app_window
        wnd_size = wnd.size()
        # create view from camera and assign it to window
        wnd.wnd_handle.view = View()
        # iterale all worldRenderables
        for c in self.components:
            if c.active():
                c.OnUIRender(wnd)

    def _reload(self, other):
        self.__init__()
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
    def __init__(self, owner = None):
        super(UIRenderable._get_cls(), self).__init__(owner)
        composer.components.add(self)
        self.OnEnable.append(onComponentEnable)

    def OnUIRender(self, wnd):
        pass
