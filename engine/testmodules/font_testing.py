# tests

def text_test1():
    import engine.EngineCore as core
    core.loadModule('engine.Logging')
    core.loadModule('engine.WindowModule')
    core.loadModule('engine.IOBroker')
    core.loadModule('engine.EngineConsole')
    core.loadModule('engine.TextManager')
    core.loadModule('engine.testmodules.HelloWorldModule')
    core.loadModule('engine.ModuleStamp')
    core.run()