#   Copyright Alexander Baranin 2016

def proxy(cls):
    # deproxify parents
    desired_parents = []
    for base_class in cls.__bases__:
        if base_class.__name__ == 'Proxy':
            desired_parent = base_class._Proxy__cls
            desired_parents.append(desired_parent)
        else:
            desired_parents.append(base_class)

    # rebuild class with checked parents
    new_namespace = cls.__dict__.copy()
    if '__dict__' in new_namespace:
        del new_namespace['__dict__']
    if hasattr(cls, '__metaclass__'):
        meta = cls.__metaclass__
    else:
        meta = type
    cls = meta(cls.__name__, tuple(desired_parents), new_namespace)

    # for class attributes
    class MetaProxy(type):
        def __getattr__(_cls, name):
            return cls.__getattribute__(cls, name)

    # proxy itself
    class Proxy(metaclass=MetaProxy):
        '''Proxy for reloadable class'''
        __cls = cls

        def __init__(self, *args, **kwargs):
            _cls = Proxy.__cls
            self.__obj = _cls(self, *args, **kwargs)

        def __getattr__(self, name):
            return self.__obj.__getattribute__(name)

        def __setattr__(self, arg, value):
            if arg in ('_Proxy__obj', '__class__'):
                return super().__setattr__(arg, value)
            else:
                _cls = Proxy.__cls
                return super(_cls, self.__obj).__setattr__(arg, value)

        def _get(self):
            return self.__obj

        @classmethod
        def _get_cls(self):
            return self.__cls

        def __repr__(self):
            _cls = Proxy.__cls
            return '<' + proxy.__module__ + '.proxy(' + \
                _cls.__module__ + '.' + _cls.__name__ + ') object at ' + \
                str(hex(id(self))) + '>'

    return Proxy

@proxy
class A:
    def __init__(self, prox):
        self._proxy = prox

@proxy
class B(A):
    def __init__(self, prox):
        super(B._get_cls(), self).__init__(prox)


a = B()

print(a._get().__dict__)           # ERROR
# TypeError: descriptor '__dict__' for 'A' objects doesn't apply to 'A' object
