#   Copyright Alexander Baranin 2016

import sys

module_heap = {}
        

def reloadable(cls):
    '''Decorate class in order to make it's instances reloadable'''
    class Reloadable:
        '''Proxy for reloadable class'''
        __cls = cls

        def __init__(self, *args, **kwargs):
            # hold wrapped class object in class attribute
            _cls = Reloadable.__cls
            # allocate and initialize wrapped instance
            self.__obj = _cls.__new__(_cls)
            self.__obj.__init__(*args, **kwargs)
            # Let's register it in global hash
            self.__register()

        def __init__(self, _id, *args, **kwargs):
            '''Initialize using overridden id'''
            # hold wrapped class object in class attribute
            _cls = Reloadable.__cls
            # allocate and initialize wrapped instance
            self.__obj = _cls.__new__(_cls)
            self.__obj.__init__(*args, **kwargs)
            # Let's register it in global hash
            self.__register(_id)

        @classmethod
        def _persistent(cls, _id, *args, **kwargs):
            '''Get persistent instance from id or initialize new one.'''
            _cls = Reloadable.__cls
            mdl = _cls.__module__
            if mdl in module_heap:
                # try to find old proxy instance with same id
                old_obj = module_heap[mdl].get(_id)
                if old_obj:
                    return old_obj
            # no old object, let's create one
            return Reloadable(_id, *args, **kwargs)

        # Let's provide easy attribute lookup without get()
        def __getattr__(self, name):
            return self.__obj.__getattribute__(name)

        # Transparent attribute setter
        def __setattr__(self, arg, value):
            if arg in ('_Reloadable__obj', '__class__'):
                return super().__setattr__(arg, value)
            else:
                _cls = Reloadable.__cls
                return super(_cls, self.__obj).__setattr__(arg, value)

        def _get(self):
            '''Get managed object explicitly'''
            return self.__obj

        def _reload_instance(self):
            '''Reload __obj and __class form new module'''
            _cls = Reloadable.__cls
            mdl = sys.modules[_cls.__module__]
            new_rld_cls = getattr(mdl, _cls.__name__)
            new_cls = new_rld_cls._Reloadable__cls
            new_obj = new_cls.__new__(new_cls)
            # use default constructor (wich is required)
            new_obj.__init__()
            # check if there is reload method
            reload_method = getattr(new_obj, '_reload')
            if reload_method:
                new_obj._reload(self.__obj)
            # update wrapper class and instance
            self.__obj = new_obj
            Reloadable.__cls = new_cls
            self.__class__ = new_rld_cls

        def __register(self, _id = None):
            '''register instance in global map'''
            _cls = Reloadable.__cls
            mdl = _cls.__module__
            if not _id:
                _id = id(self)
            if mdl in module_heap:
                id_hash = module_heap[mdl]
                id_hash[_id] = self
            else:
                new_dict = {}
                new_dict[_id] = self
                module_heap[mdl] = new_dict

        def __unregister(self):
            '''unregister instance from global map'''
            _cls = Reloadable.__cls
            mdl = _cls.__module__
            if mdl in module_heap:
                id_hash = module_heap[mdl]
                del id_hash[id(self)]

        def __del__(self):
            self.__unregister()
            del self.__obj

        # string representation should be fixed
        def __repr__(self):
            _cls = Reloadable.__cls
            return '<' + reloadable.__module__ + '.reloadable(' + \
                _cls.__module__ + '.' + _cls.__name__ + ') object at ' + \
                str(hex(id(self))) + '>'

    return Reloadable

def reload_module_instances(mdl_name):
    if mdl_name in module_heap:
        dct = module_heap[mdl_name]
        for id in dct:
            rldbl = dct[id]
            rldbl._reload_instance()

@reloadable
class TestClass:
    def __init__(self, num = 3):
        self.a = num

    def prunt(self):
        print(self.a)

    def _reload(self, other):
        self.a = other.a


# tests

def testReloadable():
    a = TestClass._persistent(1337, 3)
    a.prunt()
    a._get().a = 4
    a.prunt()
    a.a = 5
    a.prunt()
    print(a)
    reload_module_instances(__name__)
    print(a)
    print(a._get())
    a = TestClass._persistent(1337, 3)
    print(a)
    print(a._get())
    a.prunt()