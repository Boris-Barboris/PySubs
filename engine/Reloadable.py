#   Copyright Alexander Baranin 2016

import sys
import weakref
import inspect
import traceback
import types

module_heap = {}
        

def reloadable(cls):
    # first let's check if cls is derived from another reloadable
    desired_parents = []
    for base_class in cls.__bases__:
        if base_class.__name__ == 'Reloadable':
            # we are indeed deriving from another reloadable
            # let's redefine cls to derive reloadable's handled class
            desired_parent = base_class._Reloadable__cls
            desired_parents.append(desired_parent)
        else:
            # ok, it just a normal base class
            desired_parents.append(base_class)
    
    # now let's redefine cls as class, derived from unproxied classes
    # there can be metaclasses other than type, but that is not handled here
    cls = type(cls.__name__, tuple(desired_parents), dict(cls.__dict__))

    # in order to provide transparrent access to class methods we need to
    # define our own metaclass
    class MetaReloadable(type):
        def __getattr__(_cls, name):
            return cls.__getattribute__(cls, name)
        # we need to handle user inheriting reloadable classes without
        # decorator, so there are no inconsistencies in the class hierarchy
        def __new__(self, name, bases, fields):
            # placeholder call to type, because it's not yet implemented
            r = type.__new__(self, name, bases, fields)
            return r

    # proxy to wrap bound methods and redirect them to proxy reloadable
    # first, and then bound to underlying object symbolically
    class MethodProxy:
        def __init__(self, proxy, methodname):
            self.proxy = proxy
            self.methodname = methodname

        def __call__(self, *args, **kwargs):
            return self.proxy.__getattr__(self.methodname)(*args, **kwargs)

        def __eq__(self, other):
            return (self.proxy is other.proxy) and \
                   (self.methodname == other.methodname)

        def __ne__(self, other):
            return not self.__eq__(other)

    '''Decorate class in order to make it's instances reloadable'''
    class Reloadable(metaclass=MetaReloadable):
        '''Proxy for reloadable class'''
        __cls = cls

        def __init__(self, *args, **kwargs):
            # hold wrapped class object in class attribute
            _cls = Reloadable.__cls
            # allocate and initialize wrapped instance
            self.__obj = _cls.__new__(_cls)
            self.__obj.__init__(self, *args, **kwargs)
            # Let's register it in global hash
            self.__register()

        def _init_id(self, _id, *args, **kwargs):
            '''Initialize using overridden id'''
            # hold wrapped class object in class attribute
            _cls = Reloadable.__cls
            # allocate and initialize wrapped instance
            self.__obj = _cls.__new__(_cls)
            self.__obj.__init__(self, *args, **kwargs)
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
            obj = Reloadable.__new__(Reloadable)
            obj._init_id(_id, *args, **kwargs)
            return obj

        # Let's provide easy attribute lookup without get()
        def __getattr__(self, name):
            return self.__obj.__getattribute__(name)                

        # Get bound method proxy
        def _mproxy(self, name):
            return MethodProxy(self, name)

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

        @classmethod
        def _get_cls(self):
            '''Get managed class explicitly'''
            return self.__cls

        def _reload_instance(self):
            '''Reload __obj and __class form new module'''
            _cls = Reloadable.__cls
            mdl = sys.modules[_cls.__module__]
            new_rld_cls = getattr(mdl, _cls.__name__)
            new_cls = new_rld_cls.__cls
            new_obj = new_cls.__new__(new_cls)
            # check if there is reload method
            reload_method = getattr(new_obj, '_reload', None)
            if reload_method:
                try:
                    new_obj._reload(self.__obj, self)
                except Exception:
                    traceback.print_exc()
                    print('trying to create new object instead of reloading')
                    self._try_init(new_obj)
            else:
                self._try_init(new_obj)
            # update wrapper class and instance
            self.__obj = new_obj
            Reloadable.__cls = new_cls
            self.__class__ = new_rld_cls

        def _try_init(self, new_obj):
            try:
                new_obj.__init__(self)
            except Exception:
                traceback.print_exc()

        def __register(self, _id = None):
            '''register proxy instance in global map'''
            _cls = Reloadable.__cls
            self.__do_register(_cls.__module__, _id)

        def __do_register(self, mdl_name, _id):
            if not _id:
                _id = id(self)
            if mdl_name in module_heap:
                id_hash = module_heap[mdl_name]
                id_hash[_id] = self
            else:
                new_dict = weakref.WeakValueDictionary()
                new_dict[_id] = self
                module_heap[mdl_name] = new_dict

        # string representation need to be alterated
        def __repr__(self):
            _cls = Reloadable.__cls
            return '<' + reloadable.__module__ + '.reloadable(' + \
                _cls.__module__ + '.' + _cls.__name__ + ') object at ' + \
                str(hex(id(self))) + '>'

    return Reloadable
    

def reload_module_instances(mdl_name):
    if mdl_name in module_heap:
        dct = module_heap[mdl_name]
        for id in list(dct):
            rldbl = dct[id]
            rldbl._reload_instance()
            
def freeze_module_instances(mdl_name):
    if mdl_name in module_heap:
        weak_dct = module_heap[mdl_name]
        str_dct = {}
        for id in weak_dct:
            rldbl = weak_dct[id]
            if rldbl:
                str_dct[id] = rldbl
        module_heap[mdl_name] = str_dct
            
def unfreeze_module_instances(mdl_name):
    if mdl_name in module_heap:
        str_dct = module_heap[mdl_name]
        weak_dct = weakref.WeakValueDictionary(str_dct)
        module_heap[mdl_name] = weak_dct
            

@reloadable
class TestClass:
    def __init__(self, proxy, num = 3):
        self.a = num

    def prunt(self):
        print(self.a)

    def _reload(self, other, proxy):
        self.a = other.a

@reloadable
class ClassB(TestClass):
    def __init__(self, proxy, num = 8):
        self.a = num


# tests
def testReloadable():
    a = TestClass._persistent(1337, 3)
    a.prunt()
    bound_method = a.prunt
    bound_method()
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
    b = ClassB._persistent(1338, 9)
    print(b)
    b.prunt()