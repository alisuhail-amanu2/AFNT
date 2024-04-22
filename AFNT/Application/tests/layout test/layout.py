from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvas, NavigationToolbar2Kivy, FigureCanvasKivyAgg
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivy.uix.tabbedpanel import TabbedPanel
from matplotlib.figure import Figure
from kivy.uix.scrollview import ScrollView
import matplotlib.pyplot as plt
from AFNT.Application.local_db import LocalDB
from water_intake import WaterIntake
from datetime import datetime
from kivy.properties import NumericProperty
from kivy.clock import Clock

Builder.load_file("layout.kv")

class Home(ScreenManager):
    def __init__(self, **kwargs):
        self.local_db = LocalDB('local_db.db')
        self.water_intake = WaterIntake(self.local_db.connection)
        super().__init__(**kwargs)
        # Clock.schedule_interval(self.plot_monthly_water_intake, 15)
        # Clock.schedule_interval(self.plot_yearly_water_intake, 2)
        
    def plot_monthly_water_intake(self):
        try:
            bx1 = self.ids.bx1
            # Clear existing graphs
            bx1.clear_widgets()
            
            # Get selected month and year
            selected_month = self.ids.month.text
            selected_year = self.ids.year.text

            # Generate graph
            fig, ax = plt.subplots(figsize=(250, 150))
            canvas = fig.canvas

            water_intake_data = self.water_intake.monthly_water_intake_data(selected_month, selected_year)
                
            plt.bar(water_intake_data[0], water_intake_data[1], color='b', alpha=0.7)
            plt.title(f'Monthly Water Intake for {selected_month}/{selected_year}')
            plt.xlabel('Day of the Month')
            plt.ylabel('Water Intake (ml)')
            plt.axhline(y=2000, color='r', linestyle='--')
            plt.xticks(water_intake_data[2])
            plt.grid(axis='y')

            canvas = FigureCanvasKivyAgg(plt.gcf())
            bx1.add_widget(canvas)
        except Exception as e:
            print("Error:", e)

    def plot_yearly_water_intake(self):
        try:
            bx1 = self.ids.bx1
            selected_year = self.ids.year.text

            
            fig1, ax1 = plt.subplots()
            canvas = fig1.canvas

            water_intake_data = self.water_intake.yearly_water_intake_graph(selected_year)

            plt.figure(figsize=(12, 8))
            plt.bar(water_intake_data[0], water_intake_data[1], color='b', alpha=0.7)
            plt.xlabel('Month')
            plt.ylabel('Average Water Intake (ml)')
            plt.title(f'Yearly Average Water Intake for {selected_year}')
            plt.xticks(range(1, 13))
            plt.grid(axis='y')
            plt.axhline(y=2000, color='r', linestyle='--')

            canvas = FigureCanvasKivyAgg(plt.gcf())
            bx1.add_widget(canvas)
        except Exception as e:
            print("Error:", e)
    
        
class Main(MDApp):
    def build(self):
        # self.icon = "/home/sharif/Desktop/Projects/graph_calculator/icon.png"
        return Home()
if __name__ == "__main__":
    Main().run()