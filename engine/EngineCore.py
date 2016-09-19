#   Copyright Alexander Baranin 2016

import importlib
import imp
import traceback
import sys

# Module register and loading section

loaded_modules = {}     # List of modules, currently loaded

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
        mdl.onLoad(sys.modules[__name__])
        return
    except BaseException as ex:
        print('Error while loading module ' + moduleName + ':\n' + str(ex))
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
            mdl.onUnload()
        except BaseException as ex:
            print('Error while unloading module ' + moduleName + 
                  ':\n' + str(ex))
        try:
            mdl = imp.reload(mdl)
            mdl.onLoad(sys.modules[__name__])
        except BaseException as ex:
            print('Error while loading module ' + moduleName + 
                  ':\n' + str(ex))
    else:
        print('EngineCore: No module ' + moduleName + ' is found, loading')
        loadModule(moduleName)

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

def run():
    '''Main function that controls code execution'''
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