#   Copyright Alexander Baranin 2016

import math

from sfml.system import Vector2
from sfml.graphics import *


def dgr2rad(dgr):
    return dgr * math.pi / 180.0

def rad2dgr(rad):
    return rad / math.pi * 180.0

def clamppi(rad):
    if rad > math.pi:
        return rad - 2.0 * math.pi
    if rad < -math.pi:
        return rad + 2.0 * math.pi
    return rad

def clamp360(dgr):
    if dgr > 180.0:
        return dgr - 360.0
    if dgr < -180:
        return dgr + 360.0
    return dgr

def sqr_len(vec):
    return vec.x * vec.x + vec.y * vec.y

def vec_len(vec):
    return math.sqrt(sqr_len(vec))

def sqr(a):
    return a * a

def clmp1(a):
    return min(1.0, max(-1.0, a))

def normalize(vec):
    lgth = vec_len(vec)
    if lgth == 0.0:
        return Vector2()
    return Vector2(vec.x / lgth, vec.y / lgth)

def rad2dgr(rad):
    return rad / math.pi * 180.0

def vecangle(vec):
    vec = normalize(vec)
    if math.fabs(vec.x) < 0.70:
        return math.copysign(math.acos(vec.x), vec.y)
    else:
        angle = math.asin(vec.y)
        if vec.x < 0.0:
            angle = math.pi - angle
        return angle

def hypercross(lhs, rhs):
    return lhs.y * rhs.x - lhs.x * rhs.y

def rect2points(rect):
    points = []
    points.append(rect.position)
    points.append(rect.position + Vector2(rect.width, 0.0))
    points.append(rect.position + rect.size)
    points.append(rect.position + Vector2(0.0, rect.height))
    return points

def points2rect(points, margin = 0.0):
    xmin = min([p.x for p in points])
    ymin = min([p.y for p in points])
    xmax = max([p.x for p in points])
    ymax = max([p.y for p in points])
    return Rectangle((xmin - margin, ymin - margin), 
                     (xmax - xmin + margin, ymax - ymin + margin))