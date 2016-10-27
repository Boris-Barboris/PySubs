#   Copyright Alexander Baranin 2016

from engine.Reloadable import reloadable


@reloadable
class GameObject:
    '''Base class for all entities in the game'''
    def __init__(self):
        self.components = []
        self.enabled = True

    def addComponent(self, cmp):
        self.components.append(cmp)
        cmp.owner = self

    def addComponent(self, cmp, proxy):
        self.components.append(cmp)
        cmp.owner = proxy

    def removeComponent(self, cmp):
        self.components.remove(cmp)
        cmp.owner = None

    def findComponents(self, ctype):
        return (x for x in self.components if isinstance(x, ctype))

    def _reload(self, other):
        self.enabled = other.enabled
        self.components = list(other.components)
             
@reloadable
class Component:
    '''Base class for all components in the game'''
    def __init__(self, owner = None):
        self.enabled = True
        self.owner = owner

    def _reload(self, other):
        self.enabled = other.enabled
        self.owner = other.owner

    def active(self):
        if self.owner:
            return self.owner.enabled and self.enabled
        return False
