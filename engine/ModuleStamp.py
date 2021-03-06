﻿#   Copyright Alexander Baranin 2016

import sys
import os.path
import time
import sfml.window

_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('IOBroker', 'engine.IOBroker'),
    ('EngineConsole', 'engine.EngineConsole'))


def onLoad(core):
    IOBroker.register_handler(handle_focus, sfml.window.FocusEvent)
    EngineConsole.register_extension(toggle_command, 'stamp')
    EngineCore.schedule_FIFO(initialize, 1000)
    
def onUnload():
    EngineConsole.unregister_extension('stamp')
    IOBroker.unregister_handler(handle_focus, sfml.window.FocusEvent)


_active = True

module_hash = {}

def initialize():
    for mdl in EngineCore.loaded_modules:
        module_hash[mdl] = time.ctime(os.path.getmtime(EngineCore.loaded_modules[mdl].__file__))
    EngineCore.unschedule_FIFO(1000)

def handle_focus(event, wnd):
    if _active and event.gained:
        Logging.logMessage('ModuleStamp checking files')
        # let's loop over loaded modules and reload those with new file stamps
        for mdl in EngineCore.loaded_modules:
            new_time = time.ctime(os.path.getmtime(EngineCore.loaded_modules[mdl].__file__))
            if not mdl in module_hash:
                module_hash[mdl] = new_time
            else:
                old_time = module_hash[mdl]
                #print("old = " + EngineCore.loaded_modules[mdl].__file__ + " " + str(old_time))
                #print("new = " + EngineCore.loaded_modules[mdl].__file__ + " " + str(new_time))
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
