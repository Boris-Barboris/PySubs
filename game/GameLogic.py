#   Copyright Alexander Baranin 2016

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('Submarine', 'game.Submarine'),
    ('FPSLabel', 'game.FPSLabel'),
    ('CameraController', 'game.CameraController'),
    ('PlayerNavigation', 'game.PlayerNavigation'))

SCHED_ORDER = 40    # standard

def onLoad(core):
    global player_sub
    player_sub = Submarine.PlayerSubmarine._persistent('GameLogic.player_sub')
    PlayerNavigation.navigator.player_vessel = player_sub
    global fps_label
    #fps_label = FPSLabel.FPSLabel._persistent('GameLogic.fps_label')
    fps_label = FPSLabel.FPSLabel()
    EngineCore.schedule_FIFO(run, SCHED_ORDER)

def onUnload():
    EngineCore.unschedule_FIFO(SCHED_ORDER)

player_sub = None
fps_label = None

def run():
    player_sub.run(min(1.0 / 60.0, EngineCore.frame_time))
    fps_label.run()