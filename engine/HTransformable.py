#   Copyright Alexander Baranin 2016


from sfml.graphics import *


class HTransformable:
    def __init__(self):
        self.transformable = Transformable()
        self.parent = None

    @property
    def trmble(self):
        return self._transformable

    @property
    def ltransform(self):
        return self.transformable.transform

    @property
    def transform(self):
        if self.parent is not None:
            trans = self.parent.transform
            return trans.combine(self.transformable.transform)
        return Transform().combine(self.transformable.transform)

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

    def ltranslate(self, value):
        self.transformable.move(value)