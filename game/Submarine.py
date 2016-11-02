#   Copyright Alexander Baranin 2016

import sfml
import time
import sys
import math

from engine.GameObject import *
from engine.HTransformable import HTransformable
from engine.mathutils import *

from sfml.graphics import *
from sfml.system import *

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('WorldComposer', 'engine.WorldComposer'),
    ('OverlayComposer', 'engine.OverlayComposer'),
    ('ShipDynamics', 'game.ShipDynamics'),
    ('OverlayLabels', 'game.OverlayLabels'),
    ('ShipSteersman', 'game.ShipSteersman'))

_subscribe_modules = [
    'engine.WorldComposer',
    'engine.OverlayComposer']

from engine.EngineCore import handle_imports

handle_imports(sys.modules[__name__])


@reloadable
class PlayerSubmarine(GameObject):
    def __init__(self, proxy):
        super(PlayerSubmarine._get_cls(), self).__init__(proxy)
        Logging.logMessage('Creating player submarine')
        self.transform = HTransformable()
        self.transform.lrotation = 0.0
        self.transform.lposition = Vector2(0.0, 0.0)
        self.model = SubmarineModel()
        self.model.transform.parent = self.transform
        self.addComponent(self.model, proxy)
        self.dynamics = ShipDynamics.ShipDynamics()
        self.addComponent(self.dynamics, proxy)
        label = SubmarineLabel()
        self.addComponent(label, proxy)
        self.ctrl_state = ShipDynamics.ShipCtrlState()
        self.ctrl_state.throttle = 0.0
        self.ctrl_state.rudder = 0.0
        self.steersman = ShipSteersman.ShipSteersman(self)
        
    def run(self, dt):
        # game physics here
        self.dynamics.run(dt)
        # rotate screw axis
        self.model.screw_rot += dt * 8.0 * self.dynamics.engine_throttle
        self.model.screw_rot = clamppi(self.model.screw_rot)

    def _reload(self, other, proxy):
        super(PlayerSubmarine._get_cls(), self)._reload(other, proxy)
        self.model = other.model
        self.dynamics = other.dynamics
        self.transform = other.transform
        self.ctrl_state = other.ctrl_state
        self.ctrl_state.throttle = 1.0
        self.ctrl_state.rudder = 0.0
        self.steersman = other.steersman


@reloadable
class SubmarineModel(WorldComposer.WorldRenderable):
    def __init__(self, proxy):
        self.transform = HTransformable()
        self.init_model()
        super(SubmarineModel._get_cls(), self).__init__(proxy)        

    def init_model(self):
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
        self.blades = 7
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
        blade.outline_color = Color(20, 20, 20, 255)
        blade.outline_thickness = 0.2
        blade.point_count = len(points)
        for i in range(0, len(points)):
            blade.set_point(i, points[i])
        for i in range(0, self.blades):
            self.screw.append(i * 2.0 * math.pi / self.blades)            
        blade.origin = (0.0, -52.5)
        self.blade = blade
        self.screw_rot = 0.0    # screw rotation   

    def _reload(self, other, proxy):
        super(SubmarineModel._get_cls(), self)._reload(other, proxy)
        self.init_model()
        self.transform = other.transform
        self.screw_rot = other.screw_rot

    def boundingRect(self):
        rect = self.hull.global_bounds
        points = rect2points(rect)
        trans = self.transform.transform
        trans_points = [trans.transform_point(x) for x in points]
        brect = points2rect(trans_points, 10.0)
        return brect

    def OnWorldRender(self, wnd, camera):
        render_state = RenderStates(BlendMode.BLEND_ALPHA, 
                                        self.transform.transform)
        screw_hide_scale = 2.0
        # screw
        if camera.scale < screw_hide_scale:
            for i in range(0, self.blades):
                # calculate angles for each blade
                self.screw[i] = self.screw_rot + i * 2.0 * math.pi / self.blades
            cosscrews = [math.cos(x) for x in self.screw]   # cosines of those angles
            sinscrews = [math.sin(x) for x in self.screw]   # sines of those angles
            zorderscew = sorted(range(0, self.blades), 
                                key = lambda x: sinscrews[x])
            first_pos_sin = 0
            for i in range(0, self.blades):
                index = zorderscew[i]
                if sinscrews[index] > 0.0:
                    first_pos_sin = i
                    break
                self.blade.ratio = Vector2(cosscrews[index], 1.0)
                wnd.draw(self.blade, render_state)

        # hull before top screws
        wnd.draw(self.hull, render_state)
        wnd.draw(self.tower, render_state)

        # top screws
        if camera.scale < screw_hide_scale:
            for i in range(first_pos_sin, self.blades):
                index = zorderscew[i]
                self.blade.ratio = Vector2(cosscrews[index], 1.0)
                wnd.draw(self.blade, render_state)
        
@reloadable
class SubmarineLabel(OverlayComposer.OverlayRenderable):
    def __init__(self, proxy):
        super(SubmarineLabel._get_cls(), self).__init__(proxy)
        self.init_shape()

    def init_shape(self):
        self.shapes = OverlayLabels.submarine_label.shapes
        self.color = Color(100, 100, 255, 255)
        self.min_zoom = 1.0
        self.full_zoom = 1.5

    def _reload(self, other, proxy):
        super(SubmarineLabel._get_cls(), self)._reload(other, proxy)
        self.init_shape()

    def OnOverlayRender(self, wnd, wnd_size, camera):
        alpha = 0
        if camera.scale > self.min_zoom:
            if camera.scale <= self.full_zoom:
                alpha = 255 * (camera.scale - self.min_zoom) / \
                    (self.full_zoom - self.min_zoom)
            else:
                alpha = 255
        color = Color(self.color.r, self.color.g, self.color.b, alpha)
        screen_pos = WorldComposer.composer.world_to_screen(
            self.owner.transform.lposition)
        render_state = RenderStates(BlendMode.BLEND_ALPHA, 
                            Transform().translate(screen_pos).scale((1.1, 1.1)))
        for shape in self.shapes:
            shape.fill_color = color
            wnd.draw(shape, render_state)