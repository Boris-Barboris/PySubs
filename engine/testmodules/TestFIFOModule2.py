#   Copyright Alexander Baranin 2016

Logging = None
EngineCore = None

def onLoad(core):
    global EngineCore
    EngineCore = core
    global Logging
    Logging = EngineCore.loaded_modules['engine.Logging']
    Logging.logMessage('TestFIFOModule2.onLoad()')
    EngineCore.schedule_FIFO(run, 20)

def onUnload():
    Logging.logMessage('TestFIFOModule2.onUnload()')
    EngineCore.core.unschedule_FIFO(20)

def run():
    Logging.logMessage('dummy print from Module2')
    s = input('Q to exit: ')
    if s in ('q', 'Q'):
        EngineCore.request_shutdown()
    else:
        EngineCore.reloadModule('engine.testmodules.TestFIFOModule1')