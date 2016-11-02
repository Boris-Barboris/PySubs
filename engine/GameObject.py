#   Copyright Alexander Baranin 2016

from engine.Reloadable import reloadable
from engine.Event import Event

import traceback

@reloadable
class GameObject:
    '''Base class for all entities in the game'''
    def __init__(self, proxy):
        self.components = []
        self._enabled = True
        self.OnEnable = Event()
        self._proxy = proxy

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.OnEnable(self._proxy, True)
        else:
            if self._enabled:
                self.OnEnable(self._proxy, False)
        self._enabled = value

    def addComponent(self, cmp, proxy):
        self.components.append(cmp)
        cmp.owner = proxy
        self.OnEnable.append(cmp._mproxy('onOwnerEnable'))

    def removeComponent(self, cmp):
        self.components.remove(cmp)
        cmp.owner = None
        try:
            self.OnEnable.remove(cmp._mproxy('onOwnerEnable'))
        except Exception:
            traceback.print_exc()

    def _reload(self, other, proxy):
        self._proxy = proxy
        self.components = other.components
        self._enabled = other._enabled
        self.OnEnable = other.OnEnable        
        
        
             
@reloadable
class Component:
    '''
        Base class for all components in the game. 
        Component can't exist without owner.
    '''
    def __init__(self, proxy, owner = None):
        self._enabled = True
        self.owner = owner
        self.OnEnable = Event()
        self._proxy = proxy

    @property
    def enabled(self):
        return self._enabled and self.owner.enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if self.owner.enabled:
                self.OnEnable(self._proxy, True)
        else:
            if self.enabled:
                self.OnEnable(self._proxy, False)
        self._enabled = value

    def onOwnerEnable(self, owner, val):
        if val and self._enabled:
            self.OnEnable(self._proxy, True)
        if not val and self.enabled:
            self.OnEnable(self._proxy, False)

    def _reload(self, other, proxy):
        self._proxy = proxy
        self.OnEnable = other.OnEnable
        self._enabled = other._enabled
        self.owner = other.owner
