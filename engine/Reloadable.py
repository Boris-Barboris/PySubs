#   Copyright Alexander Baranin 2016

import sys
import weakref
import inspect

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
            desired_parents.append(base_class)
    
    # now let's redefine cls as class, derived from unproxied classes
    # there can be metaclasses other than type, so we'll probably unhardcode 
    # this bit later
    cls = type(cls.__name__, tuple(desired_parents), dict(cls.__dict__))

    class MetaReloadable(type):
        def __getattr__(_cls, name):
            return cls.__getattribute__(cls, name)
        # we need to handle user inheriting reloadable classes without
        # decorator, so there are no inconsistencies in the class hierarchy
        def __new__(self, name, bases, fields):
            r = type.__new__(self, name, bases, fields)
            return r

    '''Decorate class in order to make it's instances reloadable'''
    class Reloadable(metaclass=MetaReloadable):
        '''Proxy for reloadable class'''
        __cls = cls

        def __init__(self, *args, **kwargs):
            # hold wrapped class object in class attribute
            _cls = Reloadable.__cls
            # allocate and initialize wrapped instance
            self.__obj = _cls.__new__(_cls)
            rld_cntr = getattr(self.__obj, '__init_rld__', None)
            if rld_cntr:
                self.__obj.__init_rld__(self, *args, **kwargs)
            else:
                self.__obj.__init__(*args, **kwargs)
            # Let's register it in global hash
            self.__register()

        def _init_id(self, _id, *args, **kwargs):
            '''Initialize using overridden id'''
            # hold wrapped class object in class attribute
            _cls = Reloadable.__cls
            # allocate and initialize wrapped instance
            self.__obj = _cls.__new__(_cls)
            rld_cntr = getattr(self.__obj, '__init_rld__', None)
            if rld_cntr:
                self.__obj.__init_rld__(self, *args, **kwargs)
            else:
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
            obj = Reloadable.__new__(Reloadable)
            obj._init_id(_id, *args, **kwargs)
            return obj

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
            # use default constructor (wich is required)
            rld_cntr = getattr(new_obj, '__init_rld__', None)
            if rld_cntr:
                new_obj.__init_rld__(self)
            else:
                new_obj.__init__()
            # check if there is reload method
            reload_method = getattr(new_obj, '_reload', None)
            if reload_method:
                try:
                    new_obj._reload(self.__obj)
                except Exception:
                    pass
            # update wrapper class and instance
            self.__obj = new_obj
            Reloadable.__cls = new_cls
            self.__class__ = new_rld_cls

        def __register(self, _id = None):
            '''register instance in global map'''
            _cls = Reloadable.__cls
            # since we support inheritance, we need to build a set of modules,
            # that are used in this class hierarchy
            #module_set = set()
            #for base_class in inspect.getmro(_cls):
            #    if base_class != object:
            #        module_set.add(base_class.__module__)
            #for mdl in module_set:
                # subscribe on all base class modules reloading
                    #self.__do_register(mdl, _id)
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
    def __init__(self, num = 3):
        self.a = num

    def prunt(self):
        print(self.a)

    def _reload(self, other):
        self.a = other.a

class ClassB(TestClass):
    def __init__(self, num = 8):
        self.a = num


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
    b = ClassB._persistent(1338, 9)
    print(b)
    b.prunt()