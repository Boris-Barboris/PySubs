#   Copyright Alexander Baranin 2016

import sfml
import time
import math

from engine.GameObject import *
from engine.mathutils import *

from sfml.graphics import *
from sfml.system import Vector2

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'))

def onLoad(core):
    Logging.logMessage('ShipDynamics module is loading')

def onUnload():
    Logging.logMessage('ShipDynamics module is unloading')


class ShipCtrlState:
    def __init__(self):
        self.rudder = 0.0;
        self.throttle = 0.0


@reloadable
class ShipDynamics(Component):
    def __init__(self):
        super(ShipDynamics._get_cls(), self).__init__()
        self.mass = 500.0
        self.moi = 500.0
        self.velocity = Vector2(0.0, 0.0)
        self.angvel = 0.0
        self.resK = 2.5
        self.resKAoA = 1.0
        self.liftK = 10.0
        self.resRotK = 100.0
        self.rudderK = 0.05
        self.min_thrust = -350.0
        self.max_thrust = 1000.0
        self.throttle_spd = 0.5
        self.engine_throttle = 0.0

    def _reload(self, other):
        self.__init__()
        super(ShipDynamics._get_cls(), self)._reload(other)
        self.velocity = other.velocity
        self.angvel = other.angvel
        self.engine_throttle = other.engine_throttle

    def run(self, dt):
        v2 = sqr_len(self.velocity)
        vel_dir = normalize(self.velocity)

        hull_angle = dgr2rad(self.owner.rotation - 90.0)
        vel_angle = vecangle(vel_dir)
        AoA = hull_angle - vel_angle
        right_vec = Vector2(-vel_dir.y, vel_dir.x)
        lift = right_vec * self.liftK * v2 * math.sin(2.0 * AoA)

        drag = -vel_dir * v2 * (self.resK + \
            self.resKAoA * sqr(math.sin(AoA)))
        drag_torque = -self.angvel * self.resRotK
        ctrl = self.owner.ctrl_state
        rudder_torque = ctrl.rudder * v2 * self.rudderK

        # update engine throttle
        if ctrl.throttle > self.engine_throttle:
            self.engine_throttle = min(self.engine_throttle + 
                dt * self.throttle_spd, min(1.0, ctrl.throttle))
        else:
            self.engine_throttle = max(self.engine_throttle - 
                dt * self.throttle_spd, max(-1.0, ctrl.throttle))

        if self.engine_throttle >= 0.0:
            thrust = self.engine_throttle * self.max_thrust
        else:
            thrust = -self.engine_throttle * self.min_thrust
        thrust_vec = Vector2(math.cos(hull_angle), math.sin(hull_angle)) * thrust

        # integration
        self.angvel += dt * (drag_torque + rudder_torque) / self.moi
        self.velocity += (drag + thrust_vec + lift) * dt / self.mass
        self.owner.position += self.velocity * dt
        self.owner.rotation += rad2dgr(dt * self.angvel)