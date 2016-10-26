#   Copyright Alexander Baranin 2016

import sfml
import time
import sys
import math

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
        self.rotation = 0.0
        self.model = SubmarineModel()
        self.addComponent(self.model, proxy)
        
    def run(self, dt):
        # game physics here
        self.model.screw_rot += dt * 3.0
        if (self.model.screw_rot > 2 * math.pi):
            self.model.screw_rot -= 2 * math.pi

    def _reload(self, other):
        super(PlayerSubmarine._get_cls(), self)._reload(other)
        self.model = other.model
        self.position = other.position
        self.rotation = other.rotation


# since we need to derive from WorldRenderable, we'll
# define SubmarineModel here
@reloadable
class SubmarineModel(WorldComposer.WorldRenderable):
    def __init__(self):
        super(SubmarineModel._get_cls(), self).__init__()
        # parts of model:

        # hull
        hull = ConvexShape()
        hull.texture = None
        hull.fill_color = Color(60, 60, 60, 255)
        hull.outline_color = Color(20, 20, 20, 255)
        hull.outline_thickness = 0.8
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

        # control tower
        tower = ConvexShape()
        tower.texture = None
        tower.fill_color = Color(58, 58, 58, 255)
        tower.outline_color = Color(30, 30, 30, 255)
        tower.outline_thickness = 0.4
        points = [
            (0, -10.0),
            (2, -9.0),
            (4, -6.5),
            (4, 5.0),
            (0, 15.0),
            ]
        # tower is symmetric:
        for i in range(len(points) - 1, 0, -1):
            points.append((-points[i][0], points[i][1]))
        tower.point_count = len(points)
        for i in range(0, len(points)):
            tower.set_point(i, points[i])
        tower.origin = (0.0, 15.0)
        self.tower = tower

        # screws
        self.blades = 5
        self.screw = []
        # common points array
        points = [
            (1.8, 0),
            (2.7, 0.0),
            (5.9, 2.8),
            (1.2, 1.25),
            ]
        blade = ConvexShape()
        blade.texture = None
        blade.fill_color = Color(80, 80, 80, 255)
        blade.outline_color = Color(0, 0, 0, 100)
        blade.outline_thickness = 0.3
        blade.point_count = len(points)
        for i in range(0, len(points)):
            blade.set_point(i, points[i])
        for i in range(0, self.blades):
            self.screw.append(i * 2.0 * math.pi / self.blades)            
        blade.origin = (0.0, -52.5)
        self.blade = blade
        self.screw_rot = 0.0    # screw rotation                    

    def _reload(self, other):
        super(SubmarineModel._get_cls(), self)._reload(other)
        self.screw_rot = other.screw_rot

    def OnWorldRender(self, wnd):
        # screw
        for i in range(0, self.blades):
            # calculate angles for each blade
            self.screw[i] = self.screw_rot + i * 2.0 * math.pi / self.blades
        cosscrews = [math.cos(x) for x in self.screw]   # cosines of those angles
        sinscrews = [math.sin(x) for x in self.screw]   # sines of those angles
        zorderscew = sorted(range(0, self.blades), 
                            key = lambda x: sinscrews[x])
        self.blade.position = self.owner.position
        self.blade.rotation = self.owner.rotation
        first_pos_sin = 0
        for i in range(0, self.blades):
            index = zorderscew[i]
            if sinscrews[index] > 0.0:
                first_pos_sin = i
                break
            self.blade.ratio = Vector2(cosscrews[index], 1.0)
            wnd.draw(self.blade)

        # hull before top screws
        self.hull.position = self.owner.position
        self.hull.rotation = self.owner.rotation
        wnd.draw(self.hull)
        self.tower.position = self.owner.position
        self.tower.rotation = self.owner.rotation
        wnd.draw(self.tower)

        # top screws
        for i in range(first_pos_sin, self.blades):
            index = zorderscew[i]
            self.blade.ratio = Vector2(cosscrews[index], 1.0)
            wnd.draw(self.blade)
        
        
        

