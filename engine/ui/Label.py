#   Copyright Alexander Baranin 2016

import sys
import sfml

from engine.Reloadable import reloadable
from engine.GameObject import *
from engine.HTransformable import *
from engine.Event import Event

from sfml.graphics import *
from sfml.system import Vector2


_import_modules = (
    ('EngineCore', 'engine.EngineCore'),
    ('Logging', 'engine.Logging'),
    ('TextManager', 'engine.TextManager'),
    ('UIComposer', 'engine.UIComposer'),
    ('InputManager', 'engine.InputManager'))

_subscribe_modules = [
    'engine.UIComposer',
    'engine.InputManager']

from engine.EngineCore import handle_imports

handle_imports(sys.modules[__name__])

def onLoad(core):
    Logging.logMessage('Label is loading')

def onUnload():
    Logging.logMessage('Label is unloading')


@reloadable
class LabelObject(GameObject):
    """Example label object"""
    def __init__(self, proxy):
        super(LabelObject._get_cls(), self).__init__(proxy)
        self.transform = HPosition()
        self._label = LabelComponent()
        self.addComponent(self._label, proxy)
        self.label.transform.parent = self.transform
        self._highlight = LabelHighlightComponent(self._label)
        self.addComponent(self._highlight, proxy)

    @property
    def label(self):
        return self._label

    @property
    def text(self):
        return self._label.text

    def _reload(self, other, proxy):
        super(LabelObject._get_cls(), self)._reload(other, proxy)
        self.transform = other.transform
        self._label = other.label
        self._highlight = other._highlight


@reloadable
class LabelComponent(UIComposer.UIRenderable):
    def __init__(self, proxy):
        super(LabelComponent._get_cls(), self).__init__(proxy)
        self.transform = HPosition()
        font = TextManager.load_font('calibri.ttf')
        self.text = Text('', font, 10)
        self.text.color = Color.WHITE
        self.OnRectUpdate = Event()

    def OnUIRender(self, wnd):
        self.text.position = self.transform.position
        wnd.draw(self.text)

    @property
    def string(self):
        return self.text.string

    @string.setter
    def string(self, value):
        self.text.string = value
        self.OnRectUpdate(self, self.transform.transform_rect(
            self.text.global_bounds))
    
    @property
    def character_size(self):
        return self.text.character_size

    @character_size.setter
    def character_size(self, value):
        self.text.character_size = value
        self.OnRectUpdate(self, self.transform.transform_rect(
            self.text.global_bounds))

    def _reload(self, other, proxy):
        super(LabelComponent._get_cls(), self)._reload(other, proxy)
        self.transform = other.transform
        self.text = other.text
        self.OnRectUpdate = other.OnRectUpdate

@reloadable
class LabelHighlightComponent(InputManager.UIInputReciever):
    def __init__(self, proxy, label):
        super(LabelHighlightComponent._get_cls(), self).__init__(proxy, 
                                                                 Rectangle())
        self.label = label
        self.label.OnRectUpdate.append(proxy.update_rect)
        self.orig_color = None
        self.highlight_color = sfml.graphics.Color.YELLOW
        self.OnMouseEnter.append(proxy.onMouseEnterHandler)
        self.OnMouseLeave.append(proxy.onMouseLeaveHandler)

    def update_rect(self, label, rect):
        self.rect = rect
        self.OnRectangleChange(self)

    def onMouseEnterHandler(self):
        self.orig_color = self.label.text.color
        self.label.text.color = self.highlight_color

    def onMouseLeaveHandler(self):
        if self.orig_color is not None:
            self.label.text.color = self.orig_color

    def _reload(self, other, proxy):
        super(LabelHighlightComponent._get_cls(), self)._reload(other, proxy)
        self.label = other.label
        self.highlight_color = other.highlight_color
        self.orig_color = other.orig_color