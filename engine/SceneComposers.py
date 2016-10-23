#   Copyright Alexander Baranin 2016

# Scene - set of objects, and rues required to render them
# We'll divide scene on three layers:
#   * WorldLayer - layer where entities, that belong to game world are rendered.
#       Scale of objects is bound to objects actual positions.
#   * OverlayLayer - layer of pseudo-UI objects, that is rendered on top of game
#       objects, but with respect to screen size.
#   * UILayer - screen-space oriented layer for UI elements.
#
# This module defines prototypes for each of those layer managers and stores
# and calls singletons of such managers.

from engine.Reloadable import reloadable

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'))

SCHED_ORDER = 40

def onLoad(core):
    Logging.logMessage('SceneComposer is loading')
    global composers
    composers = Composers._persistent('ScneneComposer.composers')
    EngineCore.schedule_FIFO(run, SCHED_ORDER)

def onUnload(core):
    Logging.logMessage('SceneComposer is unloading')
    EngineCore.unschedule_FIFO(SCHED_ORDER)


composers = None

@reloadable
class Composers:
    def __init__(self):
        self.WorldLayer = None
        self.OverlayLayer = None
        self.UILayer = None

    def _reload(self, other):
        self.WorldLayer = other.WorldLayer
        self.OverlayLayer = other.OverlayLayer
        self.UILayer = other.UILayer

    def run(self):
        if (self.WorldLayer):
            self.WorldLayer.run()
        if (self.OverlayLayer):
            self.OverlayLayer.run()
        if (self.UILayer):
            self.UILayer.run()

def run():
    composers.run()