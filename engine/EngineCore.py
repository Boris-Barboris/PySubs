#   Copyright Alexander Baranin 2016

import importlib
import imp
import traceback
import sys
import time

from engine.Reloadable import freeze_module_instances, \
    unfreeze_module_instances, reload_module_instances

# Module register and loading section

loaded_modules = {}     # List of engine-handled modules, currently loaded
module_subscriptions = {}   # hash of module reloading subscriptions

def loadModule(moduleName):
    '''Dynamically load engine module'''
    if moduleName == __name__:
        print('EngineCore: cannot load EngineCore')
        return
    print('EngineCore: Loading module ' + moduleName)
    if moduleName in loaded_modules:
        print('EngineCore: Module ' + moduleName + ' is already loaded')
        return
    try:
        mdl = importlib.import_module(moduleName)
        loaded_modules[moduleName] = mdl
        handle_imports(mdl)
        mdl.onLoad(sys.modules[__name__])
        return
    except BaseException as ex:
        print('Error while loading module ' + moduleName + ':\n' + str(ex))
        loaded_modules.pop(moduleName, None)
        traceback.print_exc()
        raise
        


def reloadModule(moduleName):
    '''Reload engine module'''
    if moduleName == __name__:
        print('EngineCore: cannot load EngineCore')
        return
    if moduleName in loaded_modules:
        print('EngineCore: Reloading module ' + moduleName)
        mdl = loaded_modules[moduleName]
        try:
            freeze_module_instances(moduleName)
            mdl.onUnload()
        except BaseException as ex:
            print('Error while unloading module ' + moduleName + 
                  ':\n' + str(ex))
            traceback.print_exc()
        try:
            mdl = imp.reload(mdl)
            handle_imports(mdl)
            mdl.onLoad(sys.modules[__name__])
            reload_module_instances(moduleName)
            unfreeze_module_instances(moduleName)
            # now handle subscriptions
            if moduleName in module_subscriptions:
                for subscriber in module_subscriptions[moduleName]:
                    reloadModule(subscriber)
        except BaseException as ex:
            print('Error while loading module ' + moduleName + 
                  ':\n' + str(ex))
            traceback.print_exc()
    else:
        print('EngineCore: No module ' + moduleName + ' is found, loading')
        loadModule(moduleName)


def handle_imports(module):
    imports = getattr(module, '_import_modules', None)
    if imports:
        for pair in imports:
            if pair[1] == 'engine.EngineCore':
                setattr(module, pair[0], sys.modules[__name__])
                continue
            if not pair[1] in loaded_modules:
                loadModule(pair[1])
            setattr(module, pair[0], loaded_modules[pair[1]])
    subscriptions = getattr(module, '_subscribe_modules', None)
    if subscriptions:
        for mdl_name in subscriptions:
            if mdl_name in loaded_modules:
                if mdl_name in module_subscriptions:
                    module_subscriptions[mdl_name].add(module.__name__)
                else:
                    module_subscriptions[mdl_name] = { module.__name__ }

# Scheduling and execution section

fifo_queue = {}
ordered_fifo_ids = []

def schedule_FIFO(func, order):
    '''Register function for scheduling in FIFO queue'''
    if order in fifo_queue:
        print('EngineCore: scheduling slot is already occupied, overwriting')
    fifo_queue[order] = func
    global ordered_fifo_ids
    ordered_fifo_ids.append(order)
    ordered_fifo_ids.sort()

def unschedule_FIFO(order):
    '''Unregister function from FIFO queue'''
    if not order in fifo_queue:
        print('EngineCore: cannot unschedule something that is absent')
    else:
        del fifo_queue[order]
        ordered_fifo_ids.remove(order)

_shutdown_flag = False

def request_shutdown():
    global _shutdown_flag
    _shutdown_flag = True

_time_hp = None
frame_time = 0.0

def run():
    '''Main function that controls code execution'''
    global _time_hp
    if _time_hp is None:
        _time_hp = time.clock()
    while True:
        for order_id in ordered_fifo_ids:
            func = fifo_queue[order_id]
            try:
                func()
            except BaseException as ex:
                print('Exception in scheduled method index= ' + str(order_id) + '\n' 
                      + str(ex))
                traceback.print_exc()
            if _shutdown_flag:
                print('Terminating EngineCore normally...')
                return
        new_time = time.clock()
        global frame_time
        frame_time = new_time - _time_hp
        _time_hp = new_time



# Tests

def testLoading():
    loadModule('engine.Logging')
    loadModule('engine.testmodules.TestBootstrap')
    reloadModule('engine.testmodules.TestBootstrap')
    loadModule('engine.foobar')
    print(loaded_modules)
    keys = input('Q - exit :')
    Logging = loaded_modules['engine.Logging']
    while not keys in ('q','Q'):
        reloadModule('engine.Logging')
        Logging.logMessage('test message')
        keys = input('Q - exit :')

def testFIFOScheduling():
    loadModule('engine.Logging')
    loadModule('engine.testmodules.TestFIFOModule1')
    loadModule('engine.testmodules.TestFIFOModule2')
    run()

def testWindowModule():
    loadModule('engine.Logging')
    loadModule('engine.WindowModule')
    loadModule('engine.IOBroker')
    loadModule('engine.EngineConsole') 
    run()