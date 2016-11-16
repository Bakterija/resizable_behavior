from __future__ import print_function
from kivy.core.window import Window
from kivy.uix.image import AsyncImage
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.metrics import cm


class ResizableCursor(AsyncImage):
    hidden = False
    sides = ()
    def __init__(self, resizable_sides='', **kwargs):
        super(ResizableCursor, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (cm(0.6), cm(0.6))
        self.pos_hint = (None,None)
        self.pos = (-9999, -9999)
        self.source = 'behaviors/transparent.png'

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
            self.sides = (left, right, up, down)


class ResizableBehavior(object):
    hovering = BooleanProperty(False)
    hovering_resizable = BooleanProperty(False)
    rborder = NumericProperty(cm(0.3))
    resizable_sides = StringProperty('')
    resizing_left = BooleanProperty(False)
    resizing_right = BooleanProperty(False)
    resizing_up = BooleanProperty(False)
    resizing_down = BooleanProperty(False)
    resizing = BooleanProperty(False)
    cursor = None

    def __init__(self, **kwargs):
        super(ResizableBehavior, self).__init__( **kwargs)
        Window.bind(mouse_pos = lambda obj, val: self.on_mouse_move(val))

    def on_enter(self):
        self.cursor = ResizableCursor(
            resizable_sides = self.resizable_sides,
            size_hint = (None,None),
            size = (cm(2), cm(2)),
        )
        self.add_widget(self.cursor)

    def on_leave(self):
        self.background_color = (0.7, 0.7, 0.7, 1)
        self.remove_widget(self.cursor)

    def on_enter_resizable(self):
        Window.show_cursor = False

    def on_leave_resizable(self):
        Window.show_cursor = True

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
        if self.resizing_right or self.resizing_left or  self.resizing_down or self.resizing_up:
            self.oldpos = list(self.pos)
            self.oldsize = list(self.size)
            self.resizing = True
            Window.show_cursor = False
            return True
        else:
            return super(ResizableBehavior, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.resizing:
            if self.resizing_right:
                if touch.pos[0] > self.pos[0] + (self.rborder * 3):
                    self.width = touch.pos[0] - self.pos[0]
            elif self.resizing_left:
                if touch.pos[0] < self.oldpos[0] + self.oldsize[0] - (self.rborder * 3):
                    self.pos[0] = touch.pos[0]
                    self.width = self.oldpos[0] - touch.pos[0] + self.oldsize[0]
            if self.resizing_down:
                if touch.pos[1] < self.oldpos[1] + self.oldsize[1] - (self.rborder * 3):
                    self.pos[1] = touch.pos[1]
                    self.height = self.oldpos[1] - touch.pos[1] + self.oldsize[1]
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
