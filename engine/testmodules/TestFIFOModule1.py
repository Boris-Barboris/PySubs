#   Copyright Alexander Baranin 2016

Logging = None
EngineCore = None

def onLoad(core):
    global EngineCore
    EngineCore = core
    global Logging
    Logging = EngineCore.loaded_modules['engine.Logging']
    Logging.logMessage('TestFIFOModule1.onLoad()')
    EngineCore.schedule_FIFO(run1, 10)
    EngineCore.schedule_FIFO(run2, 30)

def onUnload():
    Logging.logMessage('TestFIFOModule1.onUnload()')
    EngineCore.unschedule_FIFO(10)
    EngineCore.unschedule_FIFO(30)

def run1():
    Logging.logMessage('dummy print from Module1')

def run2():
    Logging.logMessage('another dummy print from Module1')
    raise ArithmeticError()