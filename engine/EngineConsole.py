#   Copyright Alexander Baranin 2016

import sfml.window

from engine.Reloadable import reloadable
from sfml.window import Keyboard as keyboard


import engine.Logging as Logging
import engine.EngineCore as EngineCore
import engine.IOBroker as IOBroker

SCHED_ORDER = 30

def onLoad(core):
    Logging.logMessage('EngineConsole is loading')
    EngineCore.schedule_FIFO(run, SCHED_ORDER)
    IOBroker.register_handler(keyboard_handler, sfml.window.KeyEvent)
    # now extensions
    global extensionCommands
    extensionCommands = ExtentionCommands._persistent('EngineConsole.extensionCommands')

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
            elif cmd in extensionCommands.extensions:
                extensionCommands.extensions[cmd](cmds)
        except Exception as ex:
            print('Input error')
    _active = False
    Logging.logMessage('Leaving engine console')


def keyboard_handler(event, wnd):
    if event.code == hotkey and event.pressed:
        # let's enter or leave repl
        global _active
        _active = True


# commands registered by other modules
@reloadable
class ExtentionCommands:
    def __init__(self):
        self.extensions = {}

    def _reload(self, other):
        self.extensions.update(other)

extensionCommands = None

def register_extension(f, cmd):
    extensionCommands.extensions[cmd] = f

def unregister_extension(cmd):
    del extensionCommands.extensions[cmd]