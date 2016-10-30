#   Copyright Alexander Baranin 2016


from sfml.graphics import *
from engine.Event import Event


class HTransformable:
    def __init__(self):
        self.transformable = Transformable()
        self.parent = None
        self.dirty = True

    @property
    def trmble(self):
        return self._transformable

    @property
    def ltransform(self):
        return self.transformable.transform

    @property
    def transform(self):
        if not self.dirty:
            return self._cache
        if self.parent is not None:
            trans = self.parent.transform
            return trans.combine(self.transformable.transform)
        self._cache = Transform().combine(self.transformable.transform)
        self.dirty = False
        return self._cache

    @property
    def lposition(self):
        return self.transformable.position

    @lposition.setter
    def lposition(self, value):
        self.transformable.position = value
        self.dirty = True

    @property
    def lrotation(self):
        return self.transformable.rotation

    @lrotation.setter
    def lrotation(self, value):
        self.transformable.rotation = value
        self.dirty = True

    @property
    def lratio(self):
        return self.transformable.ratio

    @lratio.setter
    def lratio(self, velue):
        self.transformable.ratio = value
        self.dirty = True

    def lrotate(self, value):
        self.transformable.rotate(value)
        self.dirty = True

    def ltranslate(self, value):
        self.transformable.move(value)
        self.dirty = True