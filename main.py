from __future__ import print_function
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import cm
from kivy.utils import platform
from behaviors.resizable import ResizableBehavior
from kivy.core.window import Window
from kivy.graphics import *


class ResizableLabel(ResizableBehavior, Label):
    pass


class ResizableButton(ResizableBehavior, Button):
    pass


class ResizableSideBar(ResizableBehavior, StackLayout):
    def __init__(self, **kwargs):
        super(ResizableSideBar, self).__init__(**kwargs)
        self.resizable_sides = 'r'

    def after_init(self, *args):
        for x in range(1, 10):
            lbl = Label(size_hint=(1, None), height=(cm(1)), text='X '+str(x))
            self.add_widget(lbl)
        self.bind(size=lambda obj, val: setattr(self.background, 'size', self.size))
        self.background = Rectangle(pos=self.pos, size=self.size)
        blue = InstructionGroup()
        blue.add(Color(0, 0, 1, 1))
        blue.add(self.background)
        self.canvas.before.add(blue)


class ResizableWidgetDemo(FloatLayout):
    def __init__(self, **kwargs):
        super(ResizableWidgetDemo, self).__init__( **kwargs)
        self.stack0 = StackLayout(size_hint=(1, 1))

        self.sidebar = ResizableSideBar(size_hint=(None, 1), width=cm(3))

        self.stack1 = StackLayout(size_hint=(None, 1))
        self.sidebar.bind(size=lambda obj, val: setattr(self.stack1, 'width', self.width - val[0]))
        rbutton = ResizableButton(
            text = 'RButton',
            resizable_sides = 'rd',
            pos = (300, 300),
            size_hint = (None, None),
            size = (cm(4), cm(4)),
            on_release = lambda x: print('ON_RELASE()')
        )
        sidelabel = ResizableLabel(
            text='SideLabel',
            resizable_sides = 'd',
            size_hint = (1, None),
            height = cm(1)
        )
        r4sides = ResizableButton(
            text = '4 Sides',
            resizable_sides = 'rdlu',
            size_hint = (None, None),
            size = (cm(2), cm(2)),
            on_release = lambda x: print('ON_RELASE()')
        )
        self.add_widget(self.stack0)
        self.stack0.add_widget(self.sidebar)
        self.stack0.add_widget(self.stack1)
        self.sidebar.add_widget(sidelabel)
        self.stack1.add_widget(rbutton)
        self.add_widget(r4sides)
        self.sidebar.after_init()
        Window.clearcolor = (0.4, 0.4, 0.4, 1)


class ResizableWidgetDemoApp(App):
    def build(self):
        return ResizableWidgetDemo()

    def on_pause(self):
        return True

    def on_resume(self):
        pass

if __name__ == '__main__':
    ResizableWidgetDemoApp().run()
