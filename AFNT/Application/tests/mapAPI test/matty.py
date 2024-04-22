import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.clock import Clock
from water_intake import WaterIntake
from AFNT.Application.local_db import LocalDB

#Graphical Imports
from kivymd.app import MDApp
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt


# db = LocalDB('local_db.db')
# water_intake = WaterIntake(db.connection)
# water_intake.monthly_water_intake_graph(1, 2024)
x = [ 1, 2, 3, 4, 5]
y = [5, 14, 7, 20, 11]

plt.plot(x,y)
plt.ylabel("y axis")
plt.xlabel("x axis")


class WelcomeScreen(Screen):
    pass

class FirstScreen(Screen):
    pass

class SecondScreen(Screen):
    pass

class ScreenManager(ScreenManager):
    pass

class Graph(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def save(self):
        pass

class Project(BoxLayout):
    pass

kv = Builder.load_file("matty.kv")

class TestApp(MDApp):
    title = "Kivy Project"

    def build(self, **kwargs):
        # db = LocalDB('local_db.db')
        # water_intake = WaterIntake(db.connection)
        # water_intake.monthly_water_intake_graph(1, 2024)
        return Project()

   
if __name__ == '__main__':
    TestApp().run()

