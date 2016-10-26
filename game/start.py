#   Copyright Alexander Baranin 2016


def bootstrap_game():
    import engine.EngineCore as core
    core.loadModule('engine.ModuleStamp')
    core.loadModule('game.CameraController')
    core.loadModule('game.GameLogic')
    core.run()