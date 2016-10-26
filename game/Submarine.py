#   Copyright Alexander Baranin 2016

import sfml
import time
import sys

from engine.GameObject import *

from sfml.graphics import *
from sfml.system import Vector2

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('WorldComposer', 'engine.WorldComposer'))

_subscribe_modules = [
    'engine.WorldComposer']

from engine.EngineCore import handle_imports

handle_imports(sys.modules[__name__])

def onLoad(core):
    Logging.logMessage('submarine module is loading')

def onUnload():
    Logging.logMessage('submarine module is unloading')


@reloadable
class PlayerSubmarine(GameObject):
    def __init_rld__(self, proxy):
        super(PlayerSubmarine._get_cls(), self).__init__()
        Logging.logMessage('Creating player submarine')
        self.position = (0.0, 0.0)
        self.rotation = 90.0
        mdl = SubmarineModel(proxy)
        self.addComponent(mdl)
        
    def run(self, dt):
        # game physics here
        pass

    def _reload(self, other):
        super(PlayerSubmarine._get_cls(), self)._reload(other)
        self.position = other.position
        self.rotation = other.rotation


# since we need to derive from WorldRenderable, we'll
# define SubmarineModel here
@reloadable
class SubmarineModel(WorldComposer.WorldRenderable):
    def __init_rld__(self, proxy, sub = None):
        super(SubmarineModel._get_cls(), self).__init_rld__(proxy, sub)
        # primitives:

        # hull
        hull = ConvexShape()
        hull.texture = None
        hull.fill_color = Color(60, 60, 60, 255)
        hull.outline_color = Color(0, 0, 0, 60)
        hull.outline_thickness = 1.0
        points = [
            (0, -30.0),
            (2.5, -29.5),
            (5, -27.5),
            (7.5, -25.0),
            (9.3, -21.0),
            (10, -17.0),
            (10, 40.0),
            (8, 50.0),
            (5, 58),
            (0, 70),
            ]
        # hull is symmetric:
        for i in range(len(points) - 1, 0, -1):
            points.append((-points[i][0], points[i][1]))
        hull.point_count = len(points)
        for i in range(0, len(points)):
            hull.set_point(i, points[i])
        hull.origin = (0.0, 15.0)
        self.hull = hull

    def OnWorldRender(self, wnd):
        self.hull.position = self.owner.position
        self.hull.rotation = self.owner.rotation
        wnd.draw(self.hull)
