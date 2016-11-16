from __future__ import print_function
from kivy.core.window import Window
from kivy.uix.image import AsyncImage
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.metrics import cm
from kivy.graphics import Rectangle
from kivy.graphics import InstructionGroup

__all__ = ('ResizableBehavior', )

class ResizableCursor(Widget):
    hidden = BooleanProperty(False)
    sides = ()
    source = StringProperty('')
    def __init__(self, parent, resizable_sides='', **kwargs):
        super(ResizableCursor, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (cm(0.6), cm(0.6))
        self.pos_hint = (None,None)
        self.pos = [-9999, -9999]
        self.source = 'behaviors/transparent.png'
        self.cnt = 0

        self.parent = parent
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
        else:
            self.pos[0] = val[0] - self.width / 2
            self.pos[1] = val[1] - self.height / 2

    def change_side(self, left, right, up, down):
        changed = False
        if self.hidden == False and self.sides != (left, right, up, down):
            if left and up or right and down:
                self.source = 'behaviors/resize2.png'
                changed = True
            elif left and down or right and up:
                self.source = 'behaviors/resize1.png'
                changed = True
            elif left or right:
                self.source = 'behaviors/resize_horizontal.png'
                changed = True
            elif up or down:
                self.source = 'behaviors/resize_vertical.png'
                changed = True
            else:
                if not any ((left, right, up, down)):
                    self.source = 'behaviors/transparent.png'
                    # self.hidden = True
                    # self.on_mouse_move((-9999, -9999))
            self.sides = (left, right, up, down)


class ResizableBehavior(object):
    hovering = BooleanProperty(False)
    hovering_resizable = BooleanProperty(False)
    rborder = NumericProperty(cm(0.5))
    resizable_sides = StringProperty('')
    resizing_left = BooleanProperty(False)
    resizing_right = BooleanProperty(False)
    resizing_up = BooleanProperty(False)
    resizing_down = BooleanProperty(False)
    resizing = BooleanProperty(False)
    dont_move = BooleanProperty(False)
    cursor = None

    def __init__(self, **kwargs):
        super(ResizableBehavior, self).__init__( **kwargs)
        Window.bind(mouse_pos = lambda obj, val: self.on_mouse_move(val))
        self.cursor = ResizableCursor(
            parent=self,
            resizable_sides = self.resizable_sides,
            size_hint = (None,None)
        )

    def on_enter(self):
        self.on_enter_resizable()
        self.check_resizable_side

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
            if self.resizing == False:
                if self.collide_point(pos[0], pos[1]) == False:
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
                if self.resizing == False:
                    chkr = self.check_resizable_side(pos)
                self.on_enter()

    def check_resizable_side(self, mpos):
        if 'l' in self.resizable_sides:
            self.resizing_left = False
            if mpos[0] > self.pos[0] and \
                mpos[0] < self.pos[0] + self.rborder:
                    self.resizing_left = True
        if 'r' in self.resizable_sides and self.resizing_left == False:
            self.resizing_right = False
            if mpos[0] < self.pos[0] + self.width and \
                mpos[0] > self.pos[0] + self.width - self.rborder:
                    self.resizing_right = True
        if 'd' in self.resizable_sides:
            self.resizing_down = False
            if mpos[1] > self.pos[1] and \
                mpos[1] < self.pos[1] + self.rborder:
                    self.resizing_down = True
        if 'u' in self.resizable_sides and self.resizing_down == False:
            self.resizing_up = False
            if mpos[1] < self.pos[1] + self.height and \
                mpos[1] > self.pos[1] + self.height - self.rborder:
                    self.resizing_up = True
        if self.cursor:
            self.cursor.change_side(self.resizing_left, self.resizing_right, self.resizing_up, self.resizing_down)
        if self.resizing_left or self.resizing_right or self.resizing_up or self.resizing_down:
            return True
        else:
            return False

    def on_touch_down(self, touch):
        if self.hovering:
            if any ([self.resizing_right, self.resizing_left, self.resizing_down, self.resizing_up]):
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
                    if self.dont_move == False:
                        self.pos[0] = touch.pos[0]
                        self.width = self.oldpos[0] - touch.pos[0] + self.oldsize[0]
                    else:
                        self.width = abs(touch.pos[0] - self.pos[0])
                        if self.width < self.rborder * 3:
                            self.width = self.rborder * 3
            if self.resizing_down:
                if touch.pos[1] < self.oldpos[1] + self.oldsize[1] - (self.rborder * 3):
                    if self.dont_move == False:
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
