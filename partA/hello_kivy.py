from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class HelloApp(App):
    def build(self):
        self.title = "Hello Kivy"
        layout = BoxLayout(orientation="vertical")
        self.label = Label(text="Hello!")
        button = Button(text="Click me")
        button.bind(on_press=self.on_click)            # event binding
        layout.add_widget(self.label)
        layout.add_widget(button)
        return layout

    def on_click(self, instance):
        self.label.text = "Button clicked!"


HelloApp().run()
