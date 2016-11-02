#   Copyright Alexander Baranin 2016

import math
from engine.mathutils import *

import sfml
from sfml.system import Vector2

from engine.Reloadable import reloadable

@reloadable
class ShipSteersman:
    def __init__(self, proxy, vessel):
        self.vessel = vessel
        self.dynamics = vessel.dynamics
    
    def steer_course(self, des_course):
        self.des_course = des_course
        cur_course = self.vessel.transform.lrotation
        rudder = steer_to_course(self.dynamics, cur_course, des_course)
        self.vessel.ctrl_state.rudder = rudder

    def _reload(self, other, proxy):
        self.vessel = other.vessel
        self.dynamics = other.dynamics
        self.des_course = getattr(other, 'des_course', 0.0)


def steer_to_course(ship_dyn, cur_course, des_course):
    err = clamppi(dgr2rad(des_course - cur_course))
    deriv = ship_dyn.angvel
    return clmp1(4.0 * err - 1.0 * deriv)