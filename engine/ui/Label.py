#   Copyright Alexander Baranin 2016

import sys

from engine.Reloadable import reloadable
from engine.GameObject import *
from engine.HTransformable import HTransformable

from sfml.graphics import *
from sfml.system import Vector2


_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('TextManager', 'engine.TextManager'),
    ('UIComposer', 'engine.UIComposer'))

_subscribe_modules = [
    'engine.UIComposer']

from engine.EngineCore import handle_imports

handle_imports(sys.modules[__name__])

def onLoad(core):
    Logging.logMessage('Label is loading')

def onUnload():
    Logging.logMessage('Label is unloading')


@reloadable
class LabelObject(GameObject):
    """Example label object"""
    def __init_rld__(self, proxy):
        super(LabelObject._get_cls(), self).__init__()
        self.transform = HTransformable()
        self._label = LabelComponent()
        self.addComponent(self._label, proxy)
        self.label.transform.parent = self.transform

    @property
    def label(self):
        return self._label

    @property
    def text(self):
        return self._label.text

    def _reload(self, other):
        super(LabelObject._get_cls(), self)._reload(other)
        self.transform = other.transform
        self._label = other.label


@reloadable
class LabelComponent(UIComposer.UIRenderable):
    def __init__(self):
        super(LabelComponent._get_cls(), self).__init__()
        self.transform = HTransformable()
        font = TextManager.load_font('calibri.ttf')
        self.text = Text('', font, 10)
        self.text.color = Color.WHITE

    def OnUIRender(self, wnd):
        render_state = RenderStates(BlendMode.BLEND_ALPHA, 
                                        self.transform.transform)
        wnd.draw(self.text, render_state)

    def _reload(self, other):
        self.__init__()
        super(LabelComponent._get_cls(), self)._reload(other)
        self.transform = other.transform
        self.text = other.text