#   Copyright Alexander Baranin 2016

import inspect

from datetime import datetime

def onLoad(core):
    print('Logging: engine.Logging module loaded')

def onUnload():
    print('Logging: engine.Logging module unloading')

def logMessage(message):
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0]).__name__
    timestring = datetime.now().time().isoformat()
    print(timestring + ' ' + str(module) + ': ' + message)