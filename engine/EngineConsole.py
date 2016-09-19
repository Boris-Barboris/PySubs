#   Copyright Alexander Baranin 2016

import sfml.window
from sfml.window import Keyboard as keyboard

Logging = None
EngineCore = None
IOBroker = None

SCHED_ORDER = 30

def onLoad(core):
    global EngineCore
    EngineCore = core
    global Logging
    Logging = EngineCore.loaded_modules['engine.Logging']
    global IOBroker
    IOBroker = EngineCore.loaded_modules['engine.IOBroker']
    Logging.logMessage('EngineConsole is loading')
    EngineCore.schedule_FIFO(run, SCHED_ORDER)
    IOBroker.register_handler(keyboard_handler, sfml.window.KeyEvent)

def onUnload():
    Logging.logMessage('EngineConsole is unloading')
    IOBroker.unregister_handler(keyboard_handler, sfml.window.KeyEvent)
    EngineCore.unschedule_FIFO(SCHED_ORDER)

_active = False
hotkey = keyboard.TILDE

def run():
    global _active
    if not _active:
        return
    # we're in repl
    Logging.logMessage('Entering engine console')
    str = ''
    while not str in ('go', 'g'):
        str = input('>>')
        cmds = str.split()
        try:
            cmd = cmds[0]
            if cmd == 'reload':
                mdl_name = cmds[1]
                EngineCore.reloadModule(mdl_name)
            elif cmd in ('shutdown', 'exit'):
                EngineCore.request_shutdown()
                return
            elif cmd == 'load':
                mdl_name = cmds[1]
                EngineCore.loadModule(mdl_name)
        except Exception as ex:
            print('Input error')
    _active = False
    Logging.logMessage('Leaving engine console')


def keyboard_handler(event, wnd):
    if event.code == hotkey and event.pressed:
        # let's enter or leave repl
        global _active
        _active = True