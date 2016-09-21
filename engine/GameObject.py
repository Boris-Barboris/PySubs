#   Copyright Alexander Baranin 2016

from engine.Reloadable import reloadable

def onLoad(core):
    pass

def onUnload():
    pass

@reloadable
class GameObject:
    '''Base class for all entities in the game'''
    def __init__(self, **kwargs):
        pass

