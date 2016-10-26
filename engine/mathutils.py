#   Copyright Alexander Baranin 2016

import math

from sfml.system import Vector2


def dgr2rad(dgr):
    return dgr * math.pi / 180.0

def sqr_len(vec):
    return vec.x * vec.x + vec.y * vec.y

def sqr(a):
    return a * a

def normalize(vec):
    vec2 = sqr_len(vec)
    lgth = math.sqrt(vec2)
    if lgth == 0.0:
        return Vector2()
    return Vector2(vec.x / lgth, vec.y / lgth)

def rad2dgr(rad):
    return rad / math.pi * 180.0

def vecangle(vec):
    vec = normalize(vec)
    if math.fabs(vec.x) < 0.65:
        return math.copysign(math.acos(vec.x), vec.y)
    else:
        angle = math.asin(vec.y)
        if vec.x < 0.0:
            angle = math.pi - angle
        return angle

def hypercross(lhs, rhs):
    return lhs.x * rhs.y - lhs.y * rhs.x
