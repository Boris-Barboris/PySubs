PySubs game concept.

1. It's a training project, with a goal to study Python programming language.

2. Opensource.

3. Portable. Currently, PySFML is used as middleware, wich is using OpenGL.
PySFML works with Python3.3 only atm.

4. Main focus on architecture. Gameplay is secondary. Assets are nonexistent.

5. Requirements for engine:
    - interactive development. Game object environment is decoupled from 
    Engine Core, objects are defined in modules that can be recompiled and 
    reloaded in the runtime. World state should be changed accordingly to 
    encorporate new code. That helps with interactively debugging parts of
    the game.
    - time management. Engine Core is module manager and scheduler. Interactive
    pausing, execution flow alteration.
    - ease of debugging. All parts of python code must be debuggable. Debugging
    itself should be handled by external tools of course, and there should be
    little problem to enter it.
    - not terrible performance.
    - 2D graphics support, 3D not needed, Audio questionable.
    - component model for game objects.

6. No formalized modular testing. Instead, interactive debugging 
mini-programs for particular modules.

7. Gameplay concepts milestone 0.1:
    - one submarine. One torpedo type. One civilian surface ship type.
    Sea of square form. Primitive civilian AI, torpedo guidance mechanism,
    simple acoustic sensors. Basic UI.


Modular architecture:

    Module - corresponds to a python module, prone to dynamic
reloading. Element of structural segregation of program code. In Python it has direct
representative in the form of "python module". It's best to understand it as 
variable namespace, wich can be loaded and unloaded in the runtime.
    Common problem in module reloading is leftover objects in foreign namespaces,
wich will stay in memory and keep old module fields, methods etc. Therefore we 
should handle object lifetime carefully. Constructor should be written in a way 
to register object in some kind of dictionary or array, specific to module.
    Module life cycle is handled by EngineCore. onLoad and onUnload functions
should be exported by all modules that want to be reloadable, and it's module's 
responsibility to handle gracefull variable initialization, restoration, destruction.
    engine.Reloadable module is providing class decorator wich will be used in
order to abstract away reloadable types with a lot of instances, referenced from
many places. It is essentially a smart proxy wrapper with transparent attribute
lookup and global object registration mechanisms, needed for underlying object reallocation 
and reinitialization after module reloading.
    

EngineCore scheduling:

    What is typical game loop made of? Handle I/O. Game logic processing.
Rendering (layered scene rendering, UI). Background long-going tasks. 
Background audio. Some tasks are strongly ordered, some are everlasting daemons. 
It's generally a hard task to make such system universally-applicable.
    It's good to notice, that for background tasks it doesn't really matter who
will handle them, since they are executed by OS scheduler's rules anyway, so
there's no real reason to escalate their creation to EngineCore. Instead, we'll
leave this task to game Modules. EngineCore scheduler on
the other hand will orchestrate synchronous parts of Module execution, in simple
FIFO manner.
    FIFO scheduler will perform sequential actions. Clients of
FIFO scheduler will request for integer-identified slot in ordered list of 
schedulable tasks. EngineCore will then iterate over them in ascending order.
    If some of those Modules needs some form of multithreading or background
processing, he is free to spawn whatever he wants on their own. It is expected
to gracefully stop or restart threads on module reload though.

Debugging:

    pdb standard module provides rich functionality, well exposed by Visual
Studio VSPT extension. All required features are present, so no additional effort
is needed from my side.

IO concept:
    
    Before defining rendering scheme, let's define our main I\O concept.
It consists of two input patterns - managed and unmanaged. Managed will be
using strong input focus, and relay window events to input reciever.
Then, if active managed reciever decides to do so, some events get forarded to
unmanaged scope and are handled there without any particular order or priority.
    Managed scope will operate with rectangular input recievers. Screen space will be
separated on rectangular Z-ordered overlapping areas - ManagedInputHandlers. One of them
or none will be focused. Abovementioned mechanics will be handled by InputManager module.

    
Component model:

    Main idea: entities are separated in order to unite common functionality
in one class, and not to replicate abstraction hierarchy of objects needlessly. 
Entity-Component Model also favours out reloadable paradigm. 
Typical game object in component model: GameObject instance, that has 
collection of Component instances - user-derived classes, that customize 
default engine Component behaviour. Components are usualy implementing inversion of 
control pattern, wich means, that their execution is governed by some 
centralized Module via standard callbacks, and not by the user himself. 
Such concept, if softened by overwrriding possibilities,
proved itself to be viable in popular game engines.
    Both base GameObject and Component classes must be implemented by engine
itself. Also, Reloadable module must be aware of the need to reload class 
hierarchies, and not only one classes. For example, if in hierarchy A->B->C
module, wich defined class B was reloaded, on it's reload all instances of classes
B and C must also be reloaded. Reloadable decorator with EngineCore reload
subscription functionality are handling this problem acceptably.

Module reloading:

    When Python is instructed to reload module, it overwrites the module's dict
from new file. All existing instances of types, defined in that module remain.
PySubs engine is using reloadable decorator from module engine.Reloadable.py
It is a proxy pattern implementation, that changes underlying instance when
it's module is reloaded.
    General info about reloadable classes:
    - all references to reloadable object should be indirect: reference 
Reloadable proxy, not instance itself.
    - attribute lookup should be transparent - hence the need in custom
metaclass and getattr overrides
    - super() is not working with reloadable, since decorator dynamically overrides
inheritance hierarchy to keep proxy type only on the top level. If you want
to get to base class method, use explicit 
super(Type._get_cls(), self).<methodname>(params). _get_cls is classmethod, that
returns underlying original type.
    - no parameterless constructors - always one parameter 'proxy', that is a
reference to proxy object, that will hold the instance, that is constructed now.
    - _reload(self, other, proxy) method is used to reload instance from the 
old one, instead of __init__ initializer. If it is not provided, parameterless
__init__(self, proxy) is tried.
    - currently, bound methods point to underlying object, wich is incorrect.
Use _mproxy(method_name) to get method, that binds symbolically via proxy. That
is the way to go when working with events.
    - you should never derive reloadable class by unreloadable one. It's not
handled, it will not work.