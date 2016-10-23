#   Copyright Alexander Baranin 2016

# World composer defines components, that are renderable in World layer

from engine.Reloadable import reloadable
from engine.GameObject import Component
from sfml.graphics import *
from sfml.system import Vector2

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('Composers', 'engine.SceneComposers'))

def onLoad(core):
    Logging.logMessage('WorldComposer is loading')
    global composer
    composer = WorldComposer._persistent('WorldComposer.composer')
    Composers.composers.WorldLayer = composer

def onUnload(core):
    Logging.logMessage('WorldComposer is unloading')


composer = None

@reloadable
class WorldComposer:
    def __init__(self):
        self.components = []

    def run(self):
        for c in self.components:
            c.OnWorldRender()

@reloadable
class WorldRenderable(Component):
    def __init__(self, owner = None):
        super(WorldRenderable, self).__init__(self, owner)
        composer.components.append(self)

    def OnWorldRender(self):
        pass
