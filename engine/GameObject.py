#   Copyright Alexander Baranin 2016

from engine.Reloadable import reloadable
from engine.Event import Event

@reloadable
class GameObject:
    '''Base class for all entities in the game'''
    def __init__(self):
        self.components = []
        self._enabled = True
        self.OnEnable = Event()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.OnEnable(self, True)
        else:
            if self._enabled:
                self.OnEnable(self, False)
        self._enabled = value

    def addComponent(self, cmp):
        """Better not use this for reloadable objects"""
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
        self.components = other.components
        self.OnEnable = other.OnEnable
        self._enabled = other._enabled
        
        
             
@reloadable
class Component:
    '''Base class for all components in the game'''
    def __init__(self, owner = None):
        self._enabled = True
        self.owner = owner
        self.OnEnable = Event()

    @property
    def enabled(self):
        return self._enabled and self.owner.enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled and self.owner.enabled:
                self.OnEnable(self, True)
        else:
            if self.enabled:
                self.OnEnable(self, False)
        self._enabled = value

    def onOnwerEnable(self, owner, val):
        if val and self._enabled:
            self.OnEnable(self, True)
        if not val and self.enabled:
            self.OnEnable(self, False)

    def _reload(self, other):
        self.OnEnable = other.OnEnable
        self._enabled = other._enabled
        self.owner = other.owner
