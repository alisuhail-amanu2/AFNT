from datetime import datetime
import sqlite3
from local_db import LocalDB

import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import Screen
from kivymd.uix.button import MDRoundFlatButton, MDTextButton, MDIconButton, MDRectangleFlatButton, MDRaisedButton
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.textfield import MDTextField
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivy.animation import Animation
from kivymd.uix.datatables import MDDataTable
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivymd.theming import ThemeManager
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField, MDTextFieldRect
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy_garden.mapview import MapView
from matplotlib.ticker import MultipleLocator

from workout_log import WorkoutLog
from workout import Workout
from exercise_log import ExerciseLog 

class WorkoutAllocateScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutAllocateScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.workout = Workout(self.local_db.connection)
        self.workout_logs = WorkoutLog(self.local_db.connection)
        self.exercise_log = ExerciseLog(self.local_db.connection)

        self.selected_rows = []
        self.selected_date = datetime.today().strftime('%d/%m/%Y')
        self.selected_time = datetime.today().strftime('%H:%M:%S')

    def switch_to_workout_history(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'workout_history_screen'
        self.clear_workout_allocate_datatable_box()
        plots_screen = self.manager.get_screen('workout_history_screen')
        plots_screen.clear_workout_log_datatable_box()
        plots_screen.create_workout_log_datatable()
        self.selected_rows.clear()

    def switch_to_workout_create(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'workout_create_screen'
        self.selected_rows.clear()
        self.clear_workout_allocate_datatable_box()

    def switch_to_exercise_create(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'exercise_create_screen'
        self.selected_rows.clear()
        self.clear_workout_allocate_datatable_box()

    def switch_to_exercise_allocate(self):
        if self.selected_rows:
            self.manager.transition.direction = 'left'
            self.manager.current = 'exercise_allocate_screen'
            plots_screen = self.manager.get_screen('exercise_allocate_screen')
            plots_screen.clear_exercise_allocate_datatable_box()
            plots_screen.create_exercise_allocate_datatable()

    def clear_workout_allocate_datatable_box(self):
        workout_allocate_datatable_box = self.ids.workout_allocate_datatable_box
        workout_allocate_datatable_box.clear_widgets()
        self.selected_rows.clear()

    # Allocate date input
    def handle_workout_allocate_date_input(self):
        if not hasattr(self, 'workout_allocate_date'):
            self.workout_allocate_date = MDDatePicker()
            self.workout_allocate_date.bind(on_save=self.workout_allocate_date_on_save, on_cancel=self.on_cancel)
        self.workout_allocate_date.open()

    def workout_allocate_date_on_save(self, instance, value, date_range):
        screen = self.manager.get_screen('workout_allocate_screen')
        self.selected_date = value.strftime("%d/%m/%Y")
        screen.ids.workout_allocate_date.text = self.selected_date
        self.clear_workout_allocate_datatable_box()
        self.create_workout_allocate_datatable()

    def handle_workout_allocate_time_input(self):
        if not hasattr(self, 'workout_allocate_time'):
            self.workout_allocate_time = MDTimePicker()
            self.workout_allocate_time.bind(on_save=self.workout_allocate_time_on_save, on_cancel=self.on_cancel)
        self.workout_allocate_time.open()

    def workout_allocate_time_on_save(self, instance, value):
        screen = self.manager.get_screen('workout_allocate_screen')
        self.selected_time = value.strftime("%H:%M:%S")
        screen.ids.workout_allocate_time.text = self.selected_time
        self.clear_workout_allocate_datatable_box()
        self.create_workout_allocate_datatable()

    def on_cancel(self, instance, value):
        instance.dismiss()

    def create_workout_allocate_datatable(self):
        screen = self.manager.get_screen('workout_allocate_screen')
        screen.ids.workout_allocate_date.text = self.selected_date
        screen.ids.workout_allocate_time.text = self.selected_time
        workout_allocate_datatable_box = self.ids.workout_allocate_datatable_box
        workout_allocate_data = self.workout.get_workout_details()

        if workout_allocate_data:
            self.workout_allocate_datatable = MDDataTable(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.95, 0.3),
                check=True,
                use_pagination=True,
                rows_num=6,
                pagination_menu_height='240dp',
                pagination_menu_pos="auto",
                background_color=[1, 0, 0, .5],
                column_data=[
                    ["ID", dp(25)],
                    ["Name", dp(25)],
                    ["Description", dp(35)],
                    ["Type", dp(25)],
                    ["Level", dp(25)],
                    ["Rating", dp(25)],
                ],
                row_data=workout_allocate_data
            )
            self.workout_allocate_datatable.bind(on_check_press=self.rows_selected)
        else:
            self.workout_allocate_datatable = Label(text='No Workouts Recorded', color = 'red', font_size = "20sp", bold = True)
            
        workout_allocate_datatable_box.add_widget(self.workout_allocate_datatable)
        self.selected_rows.clear()

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = ((row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)
        # print("self.selected_rows.", self.selected_rows)

    def remove_row(self):
        if self.selected_rows:
            # print("selected_rows:", self.selected_rows)
            for row in self.selected_rows:
                workout_id = row[0]
                self.workout.remove_workout(row[0])
        self.clear_workout_allocate_datatable_box()
        self.create_workout_allocate_datatable()
        self.selected_rows.clear()

    def update_row(self):
        if self.selected_rows:
            for selected_row in self.selected_rows:
                update_popup = UpdateWorkoutAllocatePopup(selected_row, update_workout_allocate_callback=self.update_row_callback)
                self.selected_rows.clear()
                update_popup.open()

    def update_row_callback(self, workout_id, workout_name, description, workout_type):
        # print("updated data", workout_id, workout_name, description, workout_type)

        workout_update = {
            'workout_name': workout_name,
            'description': description,
            'type': workout_type,
        }
            
        self.workout.update_workout(workout_id, workout_update)
        self.clear_workout_allocate_datatable_box()
        self.create_workout_allocate_datatable()
        self.selected_rows.clear()

    def get_selected_rows(self):
        return self.selected_rows

    def allocate_save_button(self):
        if self.selected_rows:
            # print("selected data", self.selected_rows, self.selected_date, self.selected_time)
            # print("datadata", self.selected_rows[0][0])
            insert_workout_log = {
                'workout_id': self.selected_rows[0][0],
                'date_assigned': self.selected_date,
                'time_assigned': self.selected_time,
                'is_complete': 0,
                'is_active': 1,
            }

            new_workout_log_id = self.workout_logs.insert_workout_log(insert_workout_log)
            if new_workout_log_id:
                latest_workout_log = self.workout_logs.get_latest_workout_log_id(self.selected_rows[0][0])
                # print("old workout log, new workout log", latest_workout_log, new_workout_log_id)
                self.exercise_log.allocate_exercise_logs(latest_workout_log, new_workout_log_id)
                
                self.selected_rows.clear()
                allocate_workout_success = SuccessPopup()
                allocate_workout_success.show_popup('Success', 'Workout Allocated!')
            else:
                self.selected_rows.clear()
                allocate_workout_success = FailPopup()
                allocate_workout_success.show_popup('Failed', '3 Workouts Allowed Per Day!')

    def get_selected_rows(self):
        return self.selected_rows