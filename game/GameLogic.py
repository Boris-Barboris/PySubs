#   Copyright Alexander Baranin 2016


_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('Submarine', 'game.Submarine'),
    ('FPSLabel', 'game.FPSLabel'))

SCHED_ORDER = 40    # standard

def onLoad(core):
    Logging.logMessage('gameLogic is loading')
    global player_sub
    player_sub = Submarine.PlayerSubmarine._persistent('GameLogic.player_sub')
    global fps_label
    fps_label = FPSLabel.FPSLabel()
    EngineCore.schedule_FIFO(run, SCHED_ORDER)

def onUnload():
    Logging.logMessage('gameLogic is unloading')
    EngineCore.unschedule_FIFO(SCHED_ORDER)

player_sub = None
fps_label = None

def run():
    player_sub.run(1.0 / 60.0)
    fps_label.run()