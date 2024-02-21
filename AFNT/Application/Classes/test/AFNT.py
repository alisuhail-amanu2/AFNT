from kivy.app import App
# from kivy.uix.label import Label
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_file('styles.kv')

# class MyGridLayout(Widget):

#     name = ObjectProperty(None)
#     pizza = ObjectProperty(None)
#     colour = ObjectProperty(None)

#     def press(self):
#         name = self.name.text
#         pizza = self.pizza.text
#         colour = self.colour.text

#         # self.add_widget(Label(text=f"Hello {name}, you like {pizza} and you like {colour}"))
#         print(f"Hello {name}, you like {pizza} and you like {colour}")

#         self.name.text = ""
#         self.pizza.text = ""
#         self.colour.text = ""

# class AFNT(App):
#     def build(self):
#         return MyGridLayout()
#         # return Label(text='Hello Alistana')
    
# if __name__ == '__main__':
#     AFNT().run()