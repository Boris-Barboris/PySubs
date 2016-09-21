#   Copyright Alexander Baranin 2016

import sys
import os.path
import time
import sfml.window

import engine.Logging as Logging
import engine.EngineCore as EngineCore
import engine.IOBroker as IOBroker
import engine.EngineConsole as EngineConsole

def onLoad(core):
    Logging.logMessage('ModuleStamp is loading')
    IOBroker.register_handler(handle_focus, sfml.window.FocusEvent)
    EngineConsole.register_extension(toggle_command, 'stamp')
    initialize()
    
def onUnload():
    Logging.logMessage('ModuleStamp is unloading')
    EngineConsole.unregister_extension(toggle_command, 'stamp')
    IOBroker.unregister_handler(handle_focus, sfml.window.FocusEvent)


_active = True

module_hash = {}

def initialize():
    for mdl in EngineCore.loaded_modules:
        module_hash[mdl] = time.ctime(os.path.getmtime(EngineCore.loaded_modules[mdl].__file__))

def handle_focus(event, wnd):
    if _active and event.gained:
        # let's loop over loaded modules and reload those with new file stamps
        for mdl in EngineCore.loaded_modules:
            new_time = time.ctime(os.path.getmtime(EngineCore.loaded_modules[mdl].__file__))
            if not mdl in module_hash:
                module_hash[mdl] = new_time
            else:
                old_time = module_hash[mdl]
                if new_time > old_time:
                    # let's reload module
                    EngineCore.reloadModule(mdl)
                    module_hash[mdl] = new_time

def toggle_command(cmds):
    global active
    if cmds[1] in ('on', '1'):
        _active = True
    elif cmds[1] in ('off', '0'):
        _active = False
