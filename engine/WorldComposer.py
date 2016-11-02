#   Copyright Alexander Baranin 2016

# World composer defines components, that are renderable in World layer
# We'll probably expand base classes here later

from engine.Reloadable import reloadable
from engine.GameObject import Component
from engine.SpacialHash import Fixed2DHash

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

class Camera:
    def __init__(self):
        self.position = Vector2(0, 0)
        # how many game units in 1 pixel:
        self.scale = 0.1

@reloadable
class WorldComposer:
    def __init__(self, proxy):
        self.camera = Camera()
        self.view = View()
        self.components = weakref.WeakSet()
        self.hash = Fixed2DHash((5000.0, 5000.0), (10, 10), Vector2(-2500.0, -2500.0))

    def run(self):
        wnd = WindowModule.app_window
        wnd_size = wnd.size()
        # create view from camera and assign it to window
        self.view = self.get_view(self.camera, wnd_size)
        wnd.wnd_handle.view = self.view
        # iterate all worldRenderables to update space hashing
        for comp in self.components:
            self.hash.unregister(comp, comp.hash_index)
            comp.hash_index = self.hash.register(comp.boundingRect(), comp)
        # iterale all worldRenderables under the view rectangle
        view_rect = Rectangle(self.view.center - self.view.size / 2.0, self.view.size)
        visible_cells = self.hash.under_rect(view_rect)
        for cell in visible_cells:
            if cell is not None:
                for c in sorted(cell, key = lambda x: x.getDepth()):
                    c.OnWorldRender(wnd, self.camera)

    def get_view(self, camera, wnd_size):
        return View(Rectangle(
            (self.camera.position.x - wnd_size.x * 0.5 * self.camera.scale,
             self.camera.position.y - wnd_size.y * 0.5 * self.camera.scale),
            (wnd_size.x * self.camera.scale, wnd_size.y * self.camera.scale)))

    def world_to_screen(self, world_point):
        return WindowModule.app_window.map_coords_to_pixel(world_point, self.view)

    def screen_to_world(self, screen_point):
        return WindowModule.app_window.map_pixel_to_coords(screen_point, self.view)

    def _reload(self, other, proxy):
        self.hash = other.hash
        self.camera = other.camera
        self.view = other.view
        self.components = other.components


def onComponentEnable(comp, enabled):
    if enabled:
        composer.components.add(comp)
        comp.hash_index = composer.hash.register(comp.boundingRect(), comp)
    else:
        composer.components.remove(comp)
        composer.hash.unregister(comp, comp.hash_index)

@reloadable
class WorldRenderable(Component):
    def __init__(self, proxy, owner = None):
        super(WorldRenderable._get_cls(), self).__init__(proxy, owner)        
        self.OnEnable.append(onComponentEnable)
        self.OnEnable(proxy, True)

    def boundingRect(self):
        '''get bounding rectangle, used for hashing'''
        return Rectangle()

    def getDepth(self):
        return 0.0

    def OnWorldRender(self, wnd, camera):
        pass

    def _reload(self, other, proxy):
        super(WorldRenderable._get_cls(), self)._reload(other, proxy)
        self.hash_index = other.hash_index
