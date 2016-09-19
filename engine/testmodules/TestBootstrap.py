#   Copyright Alexander Baranin 2016

Logging = None

def onLoad(core):
    global Logging
    Logging = core.loaded_modules['engine.Logging']
    Logging.logMessage('testmodules.TestBootstrap.onLoad()')

def onUnload():
    Logging.logMessage('testmodules.TestBootstrap.onUnload()')