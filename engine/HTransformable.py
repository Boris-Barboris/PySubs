#   Copyright Alexander Baranin 2016


from sfml.graphics import *
from sfml.system import Vector2
from engine.Event import Event


class HTransformable:
    def __init__(self):
        self.transformable = Transformable()
        self.parent = None

    @property
    def ltransform(self):
        return self.transformable.transform

    @property
    def transform(self):
        if self.parent is not None:
            trans = self.parent.transform
            trans.combine(self.transformable.transform)
            return trans
        return self.transformable.transform

    @property
    def lposition(self):
        return self.transformable.position

    @lposition.setter
    def lposition(self, value):
        self.transformable.position = value

    @property
    def lrotation(self):
        return self.transformable.rotation

    @lrotation.setter
    def lrotation(self, value):
        self.transformable.rotation = value

    @property
    def lratio(self):
        return self.transformable.ratio

    @lratio.setter
    def lratio(self, velue):
        self.transformable.ratio = value

    def lrotate(self, value):
        self.transformable.rotate(value)

    def lmove(self, value):
        self.transformable.move(value)


class HPosition:
    def __init__(self):
        self._position = Vector2()
        self.parent = None

    @property
    def lposition(self):
        return self._position

    @lposition.setter
    def lposition(self, value):
        self._position = value

    @property
    def position(self):
        if self.parent is not None:
            pos = self.parent.position
            return pos + self._position
        else:
            return self._position

    def lmove(self, offset):
        self._position += offset

    def transform_rect(self, rect):
        pos = rect.position
        return Rectangle(pos + self.position, rect.size)

    def transform_point(self, point):
        return self.position + point


def testTransformable():
    a = HPosition()
    b = HPosition()
    b.parent = a
    b.lposition = Vector2(3.0, 4.0)
    d = b.transform_point(Vector2(1.0, 1.0))
    e = b.position
    print(e)
    e.x = 8
    print(e)
    
    a = Transform()
    b = a
    q = b.translate(Vector2(10.0, 2.0))
    print(a)
    print(a.transform_point(Vector2(0.0, 0.0)))
    print(b.transform_point(Vector2(0.0, 0.0)))
    print(q.transform_point(Vector2(0.0, 0.0)))
    c = Transform()
    q2 = c.translate(Vector2(1.0, 1.0))
    d = c
    k = b.combine(d)
    print(b.transform_point(Vector2(0.0, 0.0)))
    print(d.transform_point(Vector2(0.0, 0.0)))
    print(k.transform_point(Vector2(0.0, 0.0)))
    pass    