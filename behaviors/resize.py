'''
Resable Behavior
===============

The :class:`~kivy.uix.behaviors.resize.ResizableBehavior`
`mixin <https://en.wikipedia.org/wiki/Mixin>`_ class provides Resize behavior.
When combined with a widget, dragging at the resize enabled widget edge defined by the
:attr:`~kivy.uix.behaviors.resize.ResizableBehavior.rborder` will resize the widget.

For an overview of behaviors, please refer to the :mod:`~kivy.uix.behaviors`
documentation.

Example
-------

The following example adds resize behavior to a sidebar to make it resizable

    from kivy.app import App
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.behaviors import ResizableBehavior
    from kivy.uix.label import Label
    from kivy.metrics import cm
    from kivy.uix.button import Button
    from kivy.graphics import *


    class ResizableSideBar(ResizableBehavior, BoxLayout):
        def __init__(self, **kwargs):
            super(ResizableSideBar, self).__init__(**kwargs)
            self.background = Rectangle(pos=self.pos, size=self.size)
            self.resizable_sides = 'r'
            for x in range(1, 10):
                lbl = Label(size_hint=(1, None), height=(cm(1)), text='Text '+str(x))
                self.add_widget(lbl)
            self.bind(size=lambda obj, val: setattr(self.background, 'size', self.size))

            instr = InstructionGroup()
            instr.add(Color(0.6, 0.6, 0.7, 1))
            instr.add(self.background)
            self.canvas.before.add(instr)

    class Sample(FloatLayout):
        def __init__(self, **kwargs):
            super(Sample, self).__init__(**kwargs)
            sidebar = ResizableSideBar(orientation='vertical', size_hint=(None, 1), width=cm(4))
            self.add_widget(sidebar)


    class SampleApp(App):
        def build(self):
            return Sample()


    SampleApp().run()

See :class:`~kivy.uix.behaviors.ResizableBehavior` for details.
'''

from __future__ import print_function
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, NumericProperty, \
    StringProperty
from kivy.metrics import cm
from kivy.graphics import Rectangle
from kivy.graphics import InstructionGroup


__all__ = ('ResizableBehavior', )


class ResizableCursor(Widget):
    '''
    The ResizableCursor is the mouse cursor

    .. versionadded:: 1.9.2
    '''

    hidden = BooleanProperty(False)
    '''State of cursors visibility
    It is switched to True when mouse is inside the widgets resize border and False when it isn't.

    :attr:`hidden` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''


    sides = ()
    source = StringProperty('')

    def __init__(self, parent, **kwargs):
        super(ResizableCursor, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.pos_hint = (None, None)
        self.source = 'behaviors/transparent.png'
        self.parent = parent
        self.size = (cm(0.6), cm(0.6))
        self.pos = [-9999, -9999]

        # Makes an instruction group with a rectangle and loads an image inside it
        # Binds its properties to mouse positional changes and events triggered
        instr = InstructionGroup()
        self.rectangle = Rectangle(pos=self.pos, size=self.size, source=self.source)
        instr.add(self.rectangle)
        self.parent.canvas.after.add(instr)
        self.bind(pos=lambda obj, val: setattr(self.rectangle, 'pos', val))
        self.bind(source=lambda obj, val: setattr(self.rectangle, 'source', val))
        self.bind(hidden=lambda obj, val: self.on_mouse_move(Window.mouse_pos))

    def on_mouse_move(self, val):
        if self.hidden:
            if self.pos[0] != -9999:
                self.pos[0] = -9999
                self.rectangle.pos = val
                self.rectangle.pos = (-9999, -9999)
        else:
            self.pos[0] = val[0] - self.width / 2.0
            self.pos[1] = val[1] - self.height / 2.0

    def change_side(self, left, right, up, down):
        # Changes images when ResizableBehavior.hovering_resizable state changes
        if not self.hidden and self.sides != (left, right, up, down):
            if left and up or right and down:
                self.source = 'behaviors/resize2.png'
            elif left and down or right and up:
                self.source = 'behaviors/resize1.png'
            elif left or right:
                self.source = 'behaviors/resize_horizontal.png'
            elif up or down:
                self.source = 'behaviors/resize_vertical.png'
            else:
                if not any((left, right, up, down)):
                    self.source = 'behaviors/transparent.png'
            self.sides = (left, right, up, down)


class ResizableBehavior(object):
    '''
    The ResizableBehavior `mixin <https://en.wikipedia.org/wiki/Mixin>`_ class provides Resize behavior.
    When combined with a widget, dragging at the resize enabled widget edge defined by the
    :attr:`~kivy.uix.behaviors.resize.ResizableBehavior.rborder` will resize the widget. Please see
    the :mod:`drag behaviors module <kivy.uix.behaviors.resize>` documentation
    for more information.

    .. versionadded:: 1.9.2
    '''

    hovering = BooleanProperty(False)
    '''State of mouse hover.
    It is switched to True when mouse is on the widget and False when it isn't

    :attr:`hovering` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    hovering_resizable = BooleanProperty(False)
    '''State of mouse hover.
    It is switched to True when mouse is inside the widgets resize border and False when it isn't.

    :attr:`hovering_resizable` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    rborder = NumericProperty(cm(0.5))
    '''Widgets resizable border size on each side.
    Minimum resizing size is limited to rborder * 3 on all sides

    :attr:`rborder` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 0.5 centimeters.
    '''

    resizable_sides = StringProperty('')
    '''Sides which can be resized and will change mouse cursor on entering.
    Insert the first letter of up, down, left, right to use.
    For example, setting it to "r" will make it resizable the right side
    and setting it to "rl" will make it resizable on the left and right sides.

    :attr:`resizable_sides` is a :class:`~kivy.properties.StringProperty` and
    defaults to "".
    '''

    resizing_left = BooleanProperty(False)
    '''A State which is enabled/disabled depending on the position relative to the left resize border
    It is switched to True when mouse is inside the left resize border and False when it isn't.
    It adjusts the mouse cursor and manages resizing when touch is moved.

    :attr:`resizing_left` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    resizing_right = BooleanProperty(False)
    '''A State which is enabled/disabled depending on the position relative to the right resize border
    It is switched to True when mouse is inside the right resize border and False when it isn't.
    It adjusts the mouse cursor and manages resizing when touch is moved.

    :attr:`resizing_right` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    resizing_up = BooleanProperty(False)
    '''A State which is enabled/disabled depending on the position relative to the upper resize border
    It is switched to True when mouse is inside the upper resize border and False when it isn't.
    It adjusts the mouse cursor and manages resizing when touch is moved.

    :attr:`resizing_up` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    resizing_down = BooleanProperty(False)
    '''A State which is enabled/disabled depending on the position relative to the lower resize border
    It is switched to True when mouse is inside the lower resize border and False when it isn't.
    It adjusts the mouse cursor and manages resizing when touch is moved.

    :attr:`resizing_down` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    resizing = BooleanProperty(False)
    '''State of widget resizing.
    It is switched to True when a resize border is touched and back to False when it is released.
    It manages resizing when touch is moved.

    :attr:`resizing` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    dont_move = BooleanProperty(False)
    '''Move widget when resizing down or left.
    Actual position has to keep position on screen when widget has a FloatLayout parent
    and is being resized.
    Resizing and changing position variables is problematic inside movement restricting widgets,
    (StackLayout, BoxLayout, others) this property disables that.

    :attr:`dont_move` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''


    def __init__(self, **kwargs):
        super(ResizableBehavior, self).__init__(**kwargs)
        Window.bind(mouse_pos=lambda obj, val: self.on_mouse_move(val))
        self.cursor = None
        self.oldpos = []
        self.oldsize = []
        self.cursor = ResizableCursor(parent=self, size_hint=(None, None), pos_hint=(None, None))

    def on_enter(self):
        self.on_enter_resizable()

    def on_leave(self):
        self.cursor.hidden = True

    def on_enter_resizable(self):
        Window.show_cursor = False
        self.cursor.hidden = False

    def on_leave_resizable(self):
        Window.show_cursor = True
        self.cursor.hidden = True

    def on_mouse_move(self, pos):
        if self.hovering:
            if self.cursor:
                self.cursor.on_mouse_move(pos)
            if not self.resizing:
                if not self.collide_point(pos[0], pos[1]):
                    self.hovering = False
                    self.on_leave()
                    self.on_leave_resizable()
                else:
                    chkr = self.check_resizable_side(pos)
                    if chkr != self.hovering_resizable:
                        self.hovering_resizable = chkr
                        if chkr:
                            self.on_enter_resizable()
                            self.cursor.hidden = False
                        else:
                            self.on_leave_resizable()
                            self.cursor.hidden = True
        else:
            if self.collide_point(pos[0], pos[1]):
                self.hovering = True
                if not self.resizing:
                    self.check_resizable_side(pos)
                self.on_enter()

    def check_resizable_side(self, mpos):
        if 'l' in self.resizable_sides:
            self.resizing_left = False
            if mpos[0] > self.pos[0]:
                if mpos[0] < self.pos[0] + self.rborder:
                    self.resizing_left = True
        if 'r' in self.resizable_sides and not self.resizing_left:
            self.resizing_right = False
            if mpos[0] < self.pos[0] + self.width:
                if mpos[0] > self.pos[0] + self.width - self.rborder:
                    self.resizing_right = True
        if 'd' in self.resizable_sides:
            self.resizing_down = False
            if mpos[1] > self.pos[1]:
                if mpos[1] < self.pos[1] + self.rborder:
                    self.resizing_down = True
        if 'u' in self.resizable_sides and not self.resizing_down:
            self.resizing_up = False
            if mpos[1] < self.pos[1] + self.height:
                if mpos[1] > self.pos[1] + self.height - self.rborder:
                    self.resizing_up = True
        if self.cursor:
            self.cursor.change_side(self.resizing_left, self.resizing_right, self.resizing_up, self.resizing_down)
        if self.resizing_left or self.resizing_right or self.resizing_up or self.resizing_down:
            return True
        else:
            return False

    def on_touch_down(self, touch):
        if self.hovering:
            if any([self.resizing_right, self.resizing_left, self.resizing_down, self.resizing_up]):
                self.oldpos = list(self.pos)
                self.oldsize = list(self.size)
                self.resizing = True
                Window.show_cursor = False
                return True
            else:
                return super(ResizableBehavior, self).on_touch_down(touch)
        else:
            return super(ResizableBehavior, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.resizing:
            if self.resizing_right:
                if touch.pos[0] > self.pos[0] + (self.rborder * 3):
                    self.width = touch.pos[0] - self.pos[0]
            elif self.resizing_left:
                if touch.pos[0] < self.oldpos[0] + self.oldsize[0] - (self.rborder * 3):
                    if not self.dont_move:
                        self.pos[0] = touch.pos[0]
                        self.width = self.oldpos[0] - touch.pos[0] + self.oldsize[0]
                    else:
                        self.width = abs(touch.pos[0] - self.pos[0])
                        if self.width < self.rborder * 3:
                            self.width = self.rborder * 3
            if self.resizing_down:
                if touch.pos[1] < self.oldpos[1] + self.oldsize[1] - (self.rborder * 3):
                    if not self.dont_move:
                        self.pos[1] = touch.pos[1]
                        self.height = self.oldpos[1] - touch.pos[1] + self.oldsize[1]
                    else:
                        self.height = abs(touch.pos[1] - self.pos[1])
                        if self.height < self.rborder * 3:
                            self.height = self.rborder * 3
            elif self.resizing_up:
                if touch.pos[1] > self.pos[1] + (self.rborder * 3):
                    self.height = touch.pos[1] - self.pos[1]
            return True
        else:
            return super(ResizableBehavior, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.resizing:
            self.resizing = False
            self.resizing_right = False
            self.resizing_left = False
            self.resizing_down = False
            self.resizing_up = False
            Window.show_cursor = True
            return True
        else:
            return super(ResizableBehavior, self).on_touch_up(touch)
