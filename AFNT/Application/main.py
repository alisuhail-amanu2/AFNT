# Kivy Libaries
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy_garden.mapview import MapView

# KivyMD Libaries
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.screen import Screen
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField, MDTextFieldRect
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRoundFlatButton, MDTextButton, MDIconButton, MDRectangleFlatButton, MDRaisedButton

# LocalDB tables
from local_db import LocalDB
from user import User
from weight import Weight
from height import Height
from bmi import BMI
from body_fat import BodyFat
from skeletal_muscle import SkeletalMuscle
from water_intake import WaterIntake
from step_count import StepCount
from workout import Workout
from workout_log import WorkoutLog
from exercise import Exercise
from exercise_log import ExerciseLog
from meal import Meal
from meal_log import MealLog
from food_item import FoodItem
from food_item_log import FoodItemLog
from arduino_watch import ArduinoWatch

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

logged_user = ''

class ClickableTextFieldRound(MDRelativeLayout):
    password_input_field = ObjectProperty()
    input_password = StringProperty('')

# Sucess Popup
class SuccessPopup(Popup):
    def show_popup(self, title, para):
        content = Label(text=para)
        popup = Popup(title=title, content=content, size_hint=(None, None), size=(400, 200))
        popup.bind(on_dismiss=self.on_popup_dismiss)
        popup.open()

    def on_popup_dismiss(self, instance):
        pass

# Fail Popup
class FailPopup(Popup):
    def show_popup(self, title, para):
        content = Label(text=para)
        popup = Popup(title=title, content=content, size_hint=(None, None), size=(400, 200))
        popup.bind(on_dismiss=self.on_popup_dismiss)
        popup.open()

    def on_popup_dismiss(self, instance):
        pass

# Popup
class PP(FloatLayout):
    popup_label = StringProperty()
    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text=message, size_hint=(0.2, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.5}))

# Popup for updating workout logs
class UpdateWorkoutLogPopup(Popup):
    def __init__(self, selected_row, update_workout_log_callback, **kwargs):
        super(UpdateWorkoutLogPopup, self).__init__(**kwargs)
        self.update_workout_log_callback = update_workout_log_callback
        self.selected_row = selected_row

        self.title = "Update Workout Log"
        self.title_color = get_color_from_hex("#000000")
        self.size_hint = (0.8, 0.45)

        self.background = 'white'

        layout = BoxLayout(orientation='vertical')

        self.date_assigned_input = MDTextField(multiline=False, text="Date Assigned")
        self.date_assigned_input.bind(focus=self.show_date_picker)
        layout.add_widget(self.date_assigned_input)
        self.date_assigned_input.text = self.selected_row[2]

        self.time_assigned_input = MDTextField(multiline=False, text="Time Assigned")
        self.time_assigned_input.bind(focus=self.show_time_picker)
        layout.add_widget(self.time_assigned_input)
        self.time_assigned_input.text = self.selected_row[3]

        self.is_complete_input = MDTextField(multiline=False, text="Is Complete")
        self.is_complete_input.bind(focus=self.show_completion_status_menu)
        layout.add_widget(self.is_complete_input)
        self.is_complete_input.text = self.selected_row[4]

        button_layout = BoxLayout(orientation='horizontal')

        save_button = Button(text="Save", background_normal='', background_color= (0.0, 0.8, 1, 1))
        save_button.bind(on_release=self.save_button_pressed)
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", background_normal='', background_color= (0.8, 0, 0, 1))
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.content = layout

    def show_date_picker(self, instance, value):
        if value:
            workout_log_date_dialog = MDDatePicker()
            workout_log_date_dialog.bind(on_save=self.set_date)
            workout_log_date_dialog.open()

    def set_date(self, instance, value, date_range):
        self.date_assigned_input.text = value.strftime("%d/%m/%Y")
        self.date_assigned_input.foreground_color = get_color_from_hex("#000000")

    def show_time_picker(self, instance, value):
        if value:
            time_dialog = MDTimePicker()
            time_dialog.bind(time=self.set_time)
            time_dialog.open()

    def set_time(self, instance, time):
        self.time_assigned_input.text = time.strftime("%H:%M:%S")
        self.time_assigned_input.foreground_color = get_color_from_hex("#000000")

    def show_completion_status_menu(self, instance, value):
        if value:
            menu_items = [
                {"viewclass": "OneLineListItem", "text": "Yes", "on_release": lambda x="Yes": self.select_completion_status(x)},
                {"viewclass": "OneLineListItem", "text": "No", "on_release": lambda x="No": self.select_completion_status(x)},
            ]
            menu = MDDropdownMenu(items=menu_items, width_mult=4)
            menu.caller = instance
            menu.open()

    def select_completion_status(self, selected_completion_status_text):
        self.is_complete_input.text = selected_completion_status_text
        self.is_complete_input.foreground_color = get_color_from_hex("#000000")

    def save_button_pressed(self, instance):
        workout_log_id = self.selected_row[0]
        date_assigned = self.date_assigned_input.text
        time_assigned = self.time_assigned_input.text
        is_complete = self.is_complete_input.text
        self.update_workout_log_callback(workout_log_id, date_assigned, time_assigned, is_complete)
        self.dismiss()

# Popup for updating allocated workouts
class UpdateWorkoutAllocatePopup(Popup):
    def __init__(self, selected_row, update_workout_allocate_callback, **kwargs):
        super(UpdateWorkoutAllocatePopup, self).__init__(**kwargs)
        self.update_workout_allocate_callback = update_workout_allocate_callback
        self.selected_row = selected_row

        self.title = "Update Workout"
        self.title_color = get_color_from_hex("#000000")
        self.size_hint = (0.8, 0.6)
        self.background = 'white'

        layout = BoxLayout(orientation='vertical')

        self.workout_name_input = MDTextField(hint_text="Enter Workout Name")
        layout.add_widget(self.workout_name_input)
        self.workout_name_input.text = self.selected_row[1]

        self.description_input = MDTextField(hint_text="Enter Description")
        layout.add_widget(self.description_input)
        self.description_input.text = self.selected_row[2]

        self.workout_type_input = MDTextField(hint_text="Select Workout Type")
        self.workout_type_input.bind(focus=self.show_workout_type_menu)
        layout.add_widget(self.workout_type_input)
        self.workout_type_input.text = self.selected_row[3]

        button_layout = BoxLayout(orientation='horizontal')

        save_button = Button(text="Save", background_normal='', background_color=(0.0, 0.8, 1, 1))
        save_button.bind(on_release=self.save_button_pressed)
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", background_normal='', background_color=(0.8, 0, 0, 1))
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.content = layout

    def show_workout_type_menu(self, instance, value):
        if value:
            menu_items = [
                {"viewclass": "OneLineListItem", "text": "Upper Body", "on_release": lambda x="Upper Body": self.select_workout_type(x)},
                {"viewclass": "OneLineListItem", "text": "Back", "on_release": lambda x="Back": self.select_workout_type(x)},
                {"viewclass": "OneLineListItem", "text": "Abdominals", "on_release": lambda x="Abdominals": self.select_workout_type(x)},
                {"viewclass": "OneLineListItem", "text": "Lower Body", "on_release": lambda x="Lower Body": self.select_workout_type(x)},
            ]
            menu = MDDropdownMenu(items=menu_items, width_mult=4)
            menu.caller = instance
            menu.open()

    def select_workout_type(self, selected_workout_type_text):
        self.workout_type_input.text = selected_workout_type_text
        self.workout_type_input.foreground_color = get_color_from_hex("#000000")

    def save_button_pressed(self, instance):
        workout_id = self.selected_row[0]
        workout_name = self.workout_name_input.text
        description = self.description_input.text
        workout_type = self.workout_type_input.text
        self.update_workout_allocate_callback(workout_id, workout_name, description, workout_type)
        self.dismiss()

# Popup for updating exercise logs
class UpdateExerciseLogPopup(Popup):
    def __init__(self, selected_row, update_exercise_log_callback, **kwargs):
        super(UpdateExerciseLogPopup, self).__init__(**kwargs)
        self.update_exercise_log_callback = update_exercise_log_callback
        self.selected_row = selected_row

        self.title = "Update Exercise Log"
        self.title_color = get_color_from_hex("#000000")
        self.size_hint = (0.8, 0.9)
        self.background = 'white'

        layout = BoxLayout(orientation='vertical')

        self.sets_input = MDTextField(hint_text="Sets", input_filter="int")
        layout.add_widget(self.sets_input)
        self.sets_input.text = self.selected_row[2]

        self.reps_input = MDTextField(hint_text="Reps", input_filter="int")
        layout.add_widget(self.reps_input)
        self.reps_input.text = self.selected_row[3]

        self.weight_input = MDTextField(hint_text="Weight (kg)", input_filter="float")
        layout.add_widget(self.weight_input)
        self.weight_input.text = self.selected_row[4]

        self.rest_input = MDTextField(hint_text="Rest (secs)", input_filter="int")
        layout.add_widget(self.rest_input)
        self.rest_input.text = self.selected_row[5]

        self.distance_input = MDTextField(hint_text="Distance (m)", input_filter="float")
        layout.add_widget(self.distance_input)
        self.distance_input.text = self.selected_row[6]

        self.rpe_input = MDTextField(hint_text="RPE", input_filter="int")
        layout.add_widget(self.rpe_input)
        self.rpe_input.text = self.selected_row[7]

        self.is_complete_input = MDTextField(hint_text="Is Complete")
        self.is_complete_input.bind(focus=self.show_completion_status_menu)
        layout.add_widget(self.is_complete_input)
        self.is_complete_input.text = self.selected_row[8]

        button_layout = BoxLayout(orientation='horizontal')

        save_button = Button(text="Save", background_normal='', background_color=(0.0, 0.8, 1, 1))
        save_button.bind(on_release=self.save_button_pressed)
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", background_normal='', background_color=(0.8, 0, 0, 1))
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)

        self.content = layout

    def validate_rpe(self, rpe):
        try:
            rpe_value = int(rpe)
            return 1 <= rpe_value <= 10
        except ValueError:
            return False

    def show_completion_status_menu(self, instance, value):
        if value:
            menu_items = [
                {"viewclass": "OneLineListItem", "text": "Yes", "on_release": lambda x="Yes": self.select_completion_status(x)},
                {"viewclass": "OneLineListItem", "text": "No", "on_release": lambda x="No": self.select_completion_status(x)},
            ]
            menu = MDDropdownMenu(items=menu_items, width_mult=4)
            menu.caller = instance
            menu.open()

    def select_completion_status(self, selected_completion_status_text):
        self.is_complete_input.text = selected_completion_status_text
        self.is_complete_input.foreground_color = get_color_from_hex("#000000")

    def save_button_pressed(self, instance):
        exercise_log_id = self.selected_row[0]
        sets = self.sets_input.text
        reps = self.reps_input.text
        weight = self.weight_input.text
        rest = self.rest_input.text
        distance = self.distance_input.text
        rpe = self.rpe_input.text
        is_complete = self.is_complete_input.text
        self.update_exercise_log_callback(exercise_log_id, sets, reps, weight, rest, distance, rpe, is_complete)
        self.dismiss()

# Popup for updating allocated exercises
class UpdateExerciseAllocatePopup(Popup):
    def __init__(self, selected_row, update_exercise_allocate_callback, **kwargs):
        super(UpdateExerciseAllocatePopup, self).__init__(**kwargs)
        self.update_exercise_allocate_callback = update_exercise_allocate_callback
        self.selected_row = selected_row

        self.title = "Update Exercise"
        self.title_color = get_color_from_hex("#000000")
        self.size_hint = (0.8, 0.9)
        self.background = 'white'

        layout = BoxLayout(orientation='vertical')

        self.exercise_name_input = MDTextField(hint_text="Enter Exercise Name")
        layout.add_widget(self.exercise_name_input)
        self.exercise_name_input.text = self.selected_row[1]

        self.description_input = MDTextField(hint_text="Enter Description")
        layout.add_widget(self.description_input)
        self.description_input.text = self.selected_row[2]

        self.exercise_type_input = MDTextField(hint_text="Select Workout Type")
        self.exercise_type_input.bind(focus=self.show_exercise_type_menu)
        layout.add_widget(self.exercise_type_input)
        self.exercise_type_input.text = self.selected_row[3]

        self.body_part_input = MDTextField(hint_text="Select Body Part")
        self.body_part_input.bind(focus=self.show_body_part_menu)
        layout.add_widget(self.body_part_input)
        self.body_part_input.text = self.selected_row[3]

        self.equipment_input = MDTextField(hint_text="Select Equipment")
        self.equipment_input.bind(focus=self.show_equipment_menu)
        layout.add_widget(self.equipment_input)
        self.equipment_input.text = self.selected_row[4]

        self.level_input = MDTextField(hint_text="Select Level")
        self.level_input.bind(focus=self.show_level_menu)
        layout.add_widget(self.level_input)
        self.level_input.text = self.selected_row[5]

        button_layout = BoxLayout(orientation='horizontal')

        save_button = Button(text="Save", background_normal='', background_color=(0.0, 0.8, 1, 1))
        save_button.bind(on_release=self.save_button_pressed)
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", background_normal='', background_color=(0.8, 0, 0, 1))
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.content = layout

    def handle_exercise_name_input(self, text):
        self.ids.exercise_name_input.error = not text
    
    def show_exercise_type_menu(self, instance, value):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Cardio", "on_release": lambda x="Cardio": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Olympic Weightlifting", "on_release": lambda x="Olympic Weightlifting": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Plyometrics", "on_release": lambda x="Plyometrics": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Powerlifting", "on_release": lambda x="Powerlifting": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Strength", "on_release": lambda x="Strength": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Stretching", "on_release": lambda x="Stretching": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Strongman", "on_release": lambda x="Strongman": self.set_selected_exercise_type(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_exercise_type(self, selected_exercise_type_text, textfield_instance):
        self.exercise_type_input.text = selected_exercise_type_text

    def show_body_part_menu(self, instance, value):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Upper Body", "on_release": lambda x="Upper Body": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Shoulders", "on_release": lambda x="Shoulders": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Chest", "on_release": lambda x="Chest": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Back", "on_release": lambda x="Back": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Abdomen", "on_release": lambda x="Abdomen": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Legs", "on_release": lambda x="Legs": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Push", "on_release": lambda x="Push": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Pull", "on_release": lambda x="Pull": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Core", "on_release": lambda x="Core": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Cardio", "on_release": lambda x="Cardio": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Custom", "on_release": lambda x="Custom": self.set_selected_body_part(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_body_part(self, selected_body_part_text, textfield_instance):
        self.body_part_input.text = selected_body_part_text

    def show_equipment_menu(self, instance, value):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Body Only", "on_release": lambda x="Body Only": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Cable", "on_release": lambda x="Cable": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Dumbbell", "on_release": lambda x="Dumbbell": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Exercise Ball", "on_release": lambda x="Exercise Ball": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "E-Z Curl Bar", "on_release": lambda x="E-Z Curl Bar": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Foam Roll", "on_release": lambda x="Foam Roll": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Kettlebells", "on_release": lambda x="Kettlebells": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Machine", "on_release": lambda x="Machine": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Medicine Ball", "on_release": lambda x="Medicine Ball": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Other", "on_release": lambda x="Other": self.set_selected_equipment(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_equipment(self, selected_equipment_text, textfield_instance):
        self.equipment_input.text = selected_equipment_text

    def show_level_menu(self, instance, value):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Beginner", "on_release": lambda x="Beginner": self.set_selected_level(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Intermediate", "on_release": lambda x="Intermediate": self.set_selected_level(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Advanced", "on_release": lambda x="Advanced": self.set_selected_level(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_level(self, selected_level_text, textfield_instance):
        self.level_input.text = selected_level_text

    def select_exercise_type(self, selected_exercise_type_text):
        self.exercise_type_input.text = selected_exercise_type_text
        self.exercise_type_input.foreground_color = get_color_from_hex("#000000")

    def save_button_pressed(self, instance):
        exercise_id = self.selected_row[0]
        exercise_name = self.exercise_name_input.text
        description = self.description_input.text
        exercise_type = self.exercise_type_input.text
        body_part = self.body_part_input.text
        equipment = self.equipment_input.text
        level = self.level_input.text
        self.update_exercise_allocate_callback(exercise_id, exercise_name, description, exercise_type, body_part, equipment, level)
        self.dismiss()

# Popup for updating meal logs
class UpdateMealLogPopup(Popup):
    def __init__(self, selected_row, update_meal_log_callback, **kwargs):
        super(UpdateMealLogPopup, self).__init__(**kwargs)
        self.update_meal_log_callback = update_meal_log_callback
        self.selected_row = selected_row

        self.title = "Update Meal Log"
        self.title_color = get_color_from_hex("#000000")
        self.size_hint = (0.8, 0.45)

        self.background = 'white'

        layout = BoxLayout(orientation='vertical')
        

        self.date_assigned_input = MDTextField(multiline=False, text="Date Assigned")
        self.date_assigned_input.bind(focus=self.show_date_picker)
        layout.add_widget(self.date_assigned_input)
        self.date_assigned_input.text = self.selected_row[9]

        self.time_assigned_input = MDTextField(multiline=False, text="Time Assigned")
        self.time_assigned_input.bind(focus=self.show_time_picker)
        layout.add_widget(self.time_assigned_input)
        self.time_assigned_input.text = self.selected_row[10]

        self.is_complete_input = MDTextField(multiline=False, text="Is Complete")
        self.is_complete_input.bind(focus=self.show_completion_status_menu)
        layout.add_widget(self.is_complete_input)
        self.is_complete_input.text = self.selected_row[11]

        button_layout = BoxLayout(orientation='horizontal')

        save_button = Button(text="Save", background_normal='', background_color= (0.0, 0.8, 1, 1))
        save_button.bind(on_release=self.save_button_pressed)
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", background_normal='', background_color= (0.8, 0, 0, 1))
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.content = layout

    def show_date_picker(self, instance, value):
        if value:
            meal_log_date_dialog = MDDatePicker()
            meal_log_date_dialog.bind(on_save=self.set_date)
            meal_log_date_dialog.open()

    def set_date(self, instance, value, date_range):
        self.date_assigned_input.text = value.strftime("%d/%m/%Y")
        self.date_assigned_input.foreground_color = get_color_from_hex("#000000")

    def show_time_picker(self, instance, value):
        if value:
            time_dialog = MDTimePicker()
            time_dialog.bind(time=self.set_time)
            time_dialog.open()

    def set_time(self, instance, time):
        self.time_assigned_input.text = time.strftime("%H:%M:%S")
        self.time_assigned_input.foreground_color = get_color_from_hex("#000000")

    def show_completion_status_menu(self, instance, value):
        if value:
            menu_items = [
                {"viewclass": "OneLineListItem", "text": "Yes", "on_release": lambda x="Yes": self.select_completion_status(x)},
                {"viewclass": "OneLineListItem", "text": "No", "on_release": lambda x="No": self.select_completion_status(x)},
            ]
            menu = MDDropdownMenu(items=menu_items, width_mult=4)
            menu.caller = instance
            menu.open()

    def select_completion_status(self, selected_completion_status_text):
        self.is_complete_input.text = selected_completion_status_text
        self.is_complete_input.foreground_color = get_color_from_hex("#000000")

    def save_button_pressed(self, instance):
        meal_log_id = self.selected_row[0]
        date_assigned = self.date_assigned_input.text
        time_assigned = self.time_assigned_input.text
        is_complete = self.is_complete_input.text

        self.update_meal_log_callback(meal_log_id, date_assigned, time_assigned, is_complete)
        self.dismiss()

class UpdateFoodItemLogPopup(Popup):
    def __init__(self, selected_row, update_food_item_log_callback, **kwargs):
        super(UpdateFoodItemLogPopup, self).__init__(**kwargs)
        self.update_food_item_log_callback = update_food_item_log_callback
        self.selected_row = selected_row

        self.title = "Update Food Item Log"
        self.title_color = get_color_from_hex("#000000")
        self.size_hint = (0.8, 0.9)
        self.background = 'white'

        layout = BoxLayout(orientation='vertical')

        self.serving = MDTextField(hint_text="Serving", input_filter="float")
        layout.add_widget(self.serving)
        self.serving.text = self.selected_row[2]

        self.is_complete_input = MDTextField(hint_text="Is Complete")
        self.is_complete_input.bind(focus=self.show_completion_status_menu)
        layout.add_widget(self.is_complete_input)
        self.is_complete_input.text = self.selected_row[10]

        button_layout = BoxLayout(orientation='horizontal')

        save_button = Button(text="Save", background_normal='', background_color=(0.0, 0.8, 1, 1))
        save_button.bind(on_release=self.save_button_pressed)
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", background_normal='', background_color=(0.8, 0, 0, 1))
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.content = layout

    def show_completion_status_menu(self, instance, value):
        if value:
            menu_items = [
                {"viewclass": "OneLineListItem", "text": "Yes", "on_release": lambda x="Yes": self.select_completion_status(x)},
                {"viewclass": "OneLineListItem", "text": "No", "on_release": lambda x="No": self.select_completion_status(x)},
            ]
            menu = MDDropdownMenu(items=menu_items, width_mult=4)
            menu.caller = instance
            menu.open()

    def select_completion_status(self, selected_completion_status_text):
        self.is_complete_input.text = selected_completion_status_text
        self.is_complete_input.foreground_color = get_color_from_hex("#000000")

    def save_button_pressed(self, instance):
        food_item_log_id = self.selected_row[0]
        serving = self.serving.text
        is_complete = self.is_complete_input.text
        self.update_food_item_log_callback(food_item_log_id, serving, is_complete)
        self.dismiss()

# Popup for updating allocated meals
class UpdateMealAllocatePopup(Popup):
    def __init__(self, selected_row, update_meal_allocate_callback, **kwargs):
        super(UpdateMealAllocatePopup, self).__init__(**kwargs)
        self.update_meal_allocate_callback = update_meal_allocate_callback
        self.selected_row = selected_row

        self.title = "Update Meal"
        self.title_color = get_color_from_hex("#000000")
        self.size_hint = (0.8, 0.6)
        self.background = 'white'

        layout = BoxLayout(orientation='vertical')

        self.meal_type_input = MDTextField(hint_text="Select Meal Type")
        self.meal_type_input.bind(focus=self.show_meal_type_menu)
        layout.add_widget(self.meal_type_input)
        self.meal_type_input.text = self.selected_row[1]

        self.description_input = MDTextField(hint_text="Enter Meal Description")
        layout.add_widget(self.description_input)
        self.description_input.text = self.selected_row[2]


        button_layout = BoxLayout(orientation='horizontal')

        save_button = Button(text="Save", background_normal='', background_color=(0.0, 0.8, 1, 1))
        save_button.bind(on_release=self.save_button_pressed)
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", background_normal='', background_color=(0.8, 0, 0, 1))
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.content = layout

    def show_meal_type_menu(self, instance, value):
        if value:
            menu_items = [
                {"viewclass": "OneLineListItem", "text": "Breakfast", "on_release": lambda x="Breakfast": self.select_meal_type(x)},
                {"viewclass": "OneLineListItem", "text": "Morning Snack", "on_release": lambda x="Morning Snack": self.select_meal_type(x)},
                {"viewclass": "OneLineListItem", "text": "Lunch", "on_release": lambda x="Lunch": self.select_meal_type(x)},
                {"viewclass": "OneLineListItem", "text": "Afternoon Snack", "on_release": lambda x="Afternoon Snack": self.select_meal_type(x)},
                {"viewclass": "OneLineListItem", "text": "Brunch", "on_release": lambda x="Brunch": self.select_meal_type(x)},
                {"viewclass": "OneLineListItem", "text": "Dinner", "on_release": lambda x="Dinner": self.select_meal_type(x)},
                {"viewclass": "OneLineListItem", "text": "Evening Snack", "on_release": lambda x="Evening Snack": self.select_meal_type(x)},
            ]
            menu = MDDropdownMenu(items=menu_items, width_mult=4)
            menu.caller = instance
            menu.open()

    def select_meal_type(self, selected_meal_type_text):
        self.meal_type_input.text = selected_meal_type_text
        self.meal_type_input.foreground_color = get_color_from_hex("#000000")

    def save_button_pressed(self, instance):
        meal_id = self.selected_row[0]
        description = self.description_input.text
        meal_type = self.meal_type_input.text
        self.update_meal_allocate_callback(meal_id, description, meal_type)
        self.dismiss()

# Class for managing the app screens
class WindowManager(ScreenManager):
    pass

# Login screen
class LoginScreen(Screen):
    def switch_to_registration(self):
        self.manager.current = 'registration_screen'

    def switch_to_dashboard(self):
        self.manager.current = 'dashboard_screen'

    def login_button_animation(self, widget, *args):
        animate = Animation(
            background_color=(0, 0, 1, 1),
            duration=0.5)
        animate.start(widget)

# Registration screen for creating new account
class RegistrationScreen(Screen):
    def switch_to_login(self):
        self.manager.current = 'login_screen'

# Dashboard screen
class DashboardScreen(Screen):
    def logout(self):
        self.manager.transition.direction = 'down'
        self.manager.current = 'login_screen'

    def switch_to_workout_history(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'workout_history_screen'
        plots_screen = self.manager.get_screen('workout_history_screen')
        plots_screen.clear_workout_log_datatable_box()
        plots_screen.create_workout_log_datatable()

    def switch_to_meal_history(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'meal_history_screen'
        plots_screen = self.manager.get_screen('meal_history_screen')
        plots_screen.clear_meal_log_datatable_box()
        plots_screen.create_meal_log_datatable()

    def switch_to_gym_finder(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'gym_finder_screen'
        
        plots_screen = self.manager.get_screen('gym_finder_screen')
        plots_screen.create_map_view()

    def switch_to_water_intake(self):
        self.manager.current = 'water_intake_screen'

    def switch_to_arduino_watch(self):
        self.manager.current = 'arduino_watch_screen'

    def switch_to_body_stats(self):
        self.manager.current = 'body_stats_screen'

# Workout History screen. This screen is responsible for managing workout logs (Display/Add/Edit/Delete etc)
class WorkoutHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutHistoryScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.workout_logs = WorkoutLog(self.local_db.connection)
        self.selected_rows = []

        self.from_selected_date = datetime.today().strftime('%d/%m/%Y')

        from_selected_date_obj = datetime.strptime(self.from_selected_date, '%d/%m/%Y')
        self.to_selected_date_obj = from_selected_date_obj + timedelta(days=7)
        self.to_selected_date = self.to_selected_date_obj.strftime('%d/%m/%Y')

    def switch_to_dashboard(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard_screen'
        self.selected_rows.clear()
        self.clear_workout_log_datatable_box()

    def switch_to_workout_allocate(self):
        self.selected_rows.clear()
        self.manager.transition.direction = 'left'
        self.manager.current = 'workout_allocate_screen'
        self.clear_workout_log_datatable_box
        
        plots_screen = self.manager.get_screen('workout_allocate_screen')
        plots_screen.clear_workout_allocate_datatable_box()
        plots_screen.create_workout_allocate_datatable()

    def switch_to_workout_manager(self):
        self.selected_rows.clear()
        self.manager.transition.direction = 'left'
        self.manager.current = 'workout_manager_screen'

    def switch_to_exercise_log(self):
        if self.selected_rows:
            self.manager.transition.direction = 'left'
            self.manager.current = 'exercise_log_screen'
            plots_screen = self.manager.get_screen('exercise_log_screen')
            plots_screen.create_exercise_log_datatable()

    def clear_workout_log_datatable_box(self):
        workout_log_datatable_box = self.ids.workout_log_datatable_box
        workout_log_datatable_box.clear_widgets()
        self.selected_rows.clear()

    # From date input
    def handle_workout_log_date_from_input(self):
        if not hasattr(self, 'workout_log_date_from_date'):
            self.workout_log_date_from_date = MDDatePicker()
            self.workout_log_date_from_date.bind(on_save=self.workout_log_date_from_on_save, on_cancel=self.on_cancel)
        self.workout_log_date_from_date.open()

    # To date input
    def handle_workout_log_date_to_input(self):
        if not hasattr(self, 'workout_log_date_to_date'):
            self.workout_log_date_to_date = MDDatePicker()
            self.workout_log_date_to_date.bind(on_save=self.workout_log_date_to_on_save, on_cancel=self.on_cancel)
        self.workout_log_date_to_date.open()

    def workout_log_date_from_on_save(self, instance, value, date_range):
        screen = self.manager.get_screen('workout_history_screen')
        self.from_selected_date = value.strftime("%d/%m/%Y")
        screen.ids.workout_log_date_from.text = self.from_selected_date
        self.clear_workout_log_datatable_box()
        self.create_workout_log_datatable()

    def workout_log_date_to_on_save(self, instance, value, date_range):
        screen = self.manager.get_screen('workout_history_screen')
        self.to_selected_date = value.strftime("%d/%m/%Y")
        screen.ids.workout_log_date_to.text = self.to_selected_date
        self.clear_workout_log_datatable_box()
        self.create_workout_log_datatable()

    def on_cancel(self, instance, value):
        instance.dismiss()

    # Creating datatable for workout logs
    def create_workout_log_datatable(self):
        screen = self.manager.get_screen('workout_history_screen')
        screen.ids.workout_log_date_from.text = self.from_selected_date
        screen.ids.workout_log_date_to.text = self.to_selected_date
        workout_log_datatable_box = self.ids.workout_log_datatable_box
        workout_log_data = self.workout_logs.get_date_selected_workout_logs(self.from_selected_date, self.to_selected_date)

        # Workout log datatable displays data like the ID, workout name, date and time assigned, as well as the completion status
        if workout_log_data:
            self.workout_log_datatable = MDDataTable(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.95, 0.3),
                check=True,
                use_pagination=True,
                rows_num=6,
                pagination_menu_height='240dp',
                pagination_menu_pos="auto",
                background_color=[1, 0, 0, .5],
                column_data=[
                    ["Log ID", dp(25)],
                    ["Name", dp(25)],
                    ["Date Assigned", dp(25)],
                    ["Time Assigned", dp(25)],
                    ["Complete", dp(25)]
                ],
                row_data=workout_log_data
            )
            self.workout_log_datatable.bind(on_check_press=self.rows_selected)
        else:
            self.workout_log_datatable = Label(text='No Workouts Recorded', color = 'red', font_size = "20sp", bold = True) # Return error message if no workout logs detected
            
        workout_log_datatable_box.add_widget(self.workout_log_datatable)

    def on_start_date_selected(self, instance, start_date):
        self.update_row_data(start_date, self.end_date_input.text)

    def on_end_date_selected(self, instance, end_date):
        self.update_row_data(self.start_date_input.text, end_date)

    # Update datatable rows
    def update_row_data(self, start_date, end_date):
        row_data = self.workout_logs.get_workout_logs_details_by_date_range(start_date, end_date)
        self.workout_log_datatable.row_data = row_data

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = (int(row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)

    def remove_row(self):
        if self.selected_rows:
            for row in self.selected_rows:
                workout_log_id = row[0]
                self.workout_logs.remove_workout_log(row[0])
        self.clear_workout_log_datatable_box()
        self.create_workout_log_datatable()
        self.selected_rows.clear()

    def update_row(self):
        if self.selected_rows:
            for selected_row in self.selected_rows:
                update_popup = UpdateWorkoutLogPopup(selected_row, update_workout_log_callback=self.update_row_callback)
                update_popup.open()

    def update_row_callback(self, workout_log_id, date_assigned, time_assigned, is_complete):
        if is_complete == 'Yes':
            updated_is_complete = 1
        else:
            updated_is_complete = 0
            
        self.workout_logs.update_workout_log( workout_log_id, date_assigned, time_assigned, updated_is_complete)
        self.clear_workout_log_datatable_box()
        self.create_workout_log_datatable()
        self.selected_rows.clear()

    def get_selected_rows(self):
        return self.selected_rows

# Workout Allocate screen. Used for allocating workouts to a selected datetime
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

    # Creates workout datatable and displays the workout ID, workout name, description, type and rating (for preset workouts)
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
            self.workout_allocate_datatable = Label(text='No Workouts Recorded', color = 'red', font_size = "20sp", bold = True) # Display error message if no workouts detected
            
        workout_allocate_datatable_box.add_widget(self.workout_allocate_datatable)
        self.selected_rows.clear()

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = ((row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)

    def remove_row(self):
        if self.selected_rows:
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

    # For updating workout stats
    def update_row_callback(self, workout_id, workout_name, description, workout_type):
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

# Workout Create screen. This screen is responsible for creating a new workout
class WorkoutCreateScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutCreateScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.workout = Workout(self.local_db.connection)
        self.select_workout_type = ""
        self.fail_popup = FailPopup()
        self.success_popup = SuccessPopup()

    def switch_to_workout_allocate(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'workout_allocate_screen'

        plots_screen = self.manager.get_screen('workout_allocate_screen')
        plots_screen.clear_workout_allocate_datatable_box()
        plots_screen.create_workout_allocate_datatable()

    def handle_workout_name_input(self, text):
        self.ids.workout_name_input.error = not text

    def show_workout_type_menu(self, instance):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Upper Body", "on_release": lambda x="Upper Body": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Shoulders", "on_release": lambda x="Shoulders": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Chest", "on_release": lambda x="Chest": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Back", "on_release": lambda x="Back": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Abdomen", "on_release": lambda x="Abdomen": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Legs", "on_release": lambda x="Legs": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Push", "on_release": lambda x="Push": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Pull", "on_release": lambda x="Pull": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Core", "on_release": lambda x="Core": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Cardio", "on_release": lambda x="Cardio": self.set_selected_workout_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Custom", "on_release": lambda x="Custom": self.set_selected_workout_type(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_workout_type(self, selected_workout_type_text, textfield_instance):
        self.ids.workout_type_input.text = selected_workout_type_text

    def show_level_menu(self, instance):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Beginner", "on_release": lambda x="Beginner": self.set_selected_level(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Intermediate", "on_release": lambda x="Intermediate": self.set_selected_level(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Advanced", "on_release": lambda x="Advanced": self.set_selected_level(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_level(self, selected_level_text, textfield_instance):
        self.ids.level_input.text = selected_level_text

    def verify_workout_create_input(self):
        workout_name = self.ids.workout_name_input.text
        workout_description = self.ids.workout_description_input.text
        workout_type = self.ids.workout_type_input.text
        workout_level = self.ids.level_input.text

        if not workout_name:
            return self.fail_popup.show_popup('Failed', 'Enter workout name')
        if not workout_type:
            return self.fail_popup.show_popup('Failed', 'Select workout type')

        workout_data = {
            "workout_name": workout_name,
            "description": workout_description,
            "type": workout_type,
            "date_created": datetime.now().strftime("%d/%m/%Y"),
            "level": workout_level,
            "rating": '',
            "rating_description": '',
            "time_created":datetime.now().strftime('%H:%M:%S'), 
            "is_active": 1,
        }
        self.workout.insert_workout(workout_data)
        return self.success_popup.show_popup('Success', 'Workout Created Successfully')

# Exercise Create screen. This screen is responsible for creating a new exercise
class ExerciseCreateScreen(Screen):
    def __init__(self, **kwargs):
        super(ExerciseCreateScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.exercise = Exercise(self.local_db.connection)
        self.exercise_log = ExerciseLog(self.local_db.connection)
        self.select_workout_type = ""
        self.fail_popup = FailPopup()
        self.success_popup = SuccessPopup()

    def switch_to_workout_allocate(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'workout_allocate_screen'

        plots_screen = self.manager.get_screen('workout_allocate_screen')
        plots_screen.clear_workout_allocate_datatable_box()
        plots_screen.create_workout_allocate_datatable()

    def handle_exercise_name_input(self, text):
        self.ids.exercise_name_input.error = not text
    
    # Exercise type dropdown
    def show_exercise_type_menu(self, instance):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Cardio", "on_release": lambda x="Cardio": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Olympic Weightlifting", "on_release": lambda x="Olympic Weightlifting": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Plyometrics", "on_release": lambda x="Plyometrics": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Powerlifting", "on_release": lambda x="Powerlifting": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Strength", "on_release": lambda x="Strength": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Stretching", "on_release": lambda x="Stretching": self.set_selected_exercise_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Strongman", "on_release": lambda x="Strongman": self.set_selected_exercise_type(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()
    
    def set_selected_exercise_type(self, selected_exercise_type_text, textfield_instance):
        self.ids.exercise_type_input.text = selected_exercise_type_text

    # Body part dropdown
    def show_body_part_menu(self, instance):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Upper Body", "on_release": lambda x="Upper Body": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Shoulders", "on_release": lambda x="Shoulders": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Chest", "on_release": lambda x="Chest": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Back", "on_release": lambda x="Back": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Abdomen", "on_release": lambda x="Abdomen": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Legs", "on_release": lambda x="Legs": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Push", "on_release": lambda x="Push": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Pull", "on_release": lambda x="Pull": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Core", "on_release": lambda x="Core": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Cardio", "on_release": lambda x="Cardio": self.set_selected_body_part(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Custom", "on_release": lambda x="Custom": self.set_selected_body_part(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_body_part(self, selected_body_part_text, textfield_instance):
        self.ids.body_part_input.text = selected_body_part_text

    # Equipment dropdown
    def show_equipment_menu(self, instance):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Body Only", "on_release": lambda x="Body Only": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Cable", "on_release": lambda x="Cable": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Dumbbell", "on_release": lambda x="Dumbbell": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Exercise Ball", "on_release": lambda x="Exercise Ball": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "E-Z Curl Bar", "on_release": lambda x="E-Z Curl Bar": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Foam Roll", "on_release": lambda x="Foam Roll": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Kettlebells", "on_release": lambda x="Kettlebells": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Machine", "on_release": lambda x="Machine": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Medicine Ball", "on_release": lambda x="Medicine Ball": self.set_selected_equipment(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Other", "on_release": lambda x="Other": self.set_selected_equipment(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_equipment(self, selected_equipment_text, textfield_instance):
        self.ids.equipment_input.text = selected_equipment_text

    # Level dropdown
    def show_level_menu(self, instance):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Beginner", "on_release": lambda x="Beginner": self.set_selected_level(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Intermediate", "on_release": lambda x="Intermediate": self.set_selected_level(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Advanced", "on_release": lambda x="Advanced": self.set_selected_level(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_level(self, selected_level_text, textfield_instance):
        self.ids.level_input.text = selected_level_text
        # print("Selected level", selected_level_text)

    # Duration input
    def handle_exercise_create_duration_input(self):
        if not hasattr(self, 'duration_input'):
            self.duration_input = MDTimePicker()
            self.duration_input.bind(on_save=self.duration_input_on_save, on_cancel=self.on_cancel)
        self.duration_input.open()

    def duration_input_on_save(self, instance, value):
        screen = self.manager.get_screen('exercise_create_screen')
        self.selected_time = value.strftime("%H:%M:%S")
        screen.ids.duration_input.text = self.selected_time

    def on_cancel(self, instance, value):
        instance.dismiss()

    # Verify exercise input data
    def verify_workout_create_input(self):
        exercise_name = self.ids.exercise_name_input.text
        workout_description = self.ids.exercise_description_input.text
        exercise_type = self.ids.exercise_type_input.text
        body_part = self.ids.body_part_input.text
        equipment = self.ids.equipment_input.text
        exercise_level = self.ids.level_input.text

        sets = self.ids.sets_input.text
        reps = self.ids.reps_input.text
        weight_kg = self.ids.weight_kg_input.text
        rest_s = self.ids.rest_s_input.text
        duration = self.ids.duration_input.text
        distance_m = self.ids.distance_input.text

        if not exercise_name:
            return self.fail_popup.show_popup('Failed', 'Enter exercise name')
        if not exercise_type:
            return self.fail_popup.show_popup('Failed', 'Select exercise type')
        if not body_part:
            return self.fail_popup.show_popup('Failed', 'Select body part')
        if not equipment:
            return self.fail_popup.show_popup('Failed', 'Select equiptment type')
        if not exercise_level:
            return self.fail_popup.show_popup('Failed', 'Select level')
        if sets:
            try:
                sets = int(sets)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Sets must be an integer')
        if reps:
            try:
                reps = int(reps)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Reps must be an integer')
        if rest_s:
            try:
                rest_s = int(rest_s)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Rest must be an integer')
        if weight_kg:
            try:
                weight_kg = float(weight_kg)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Weight must be a number')
        if distance_m:
            try:
                distance_m = float(distance_m)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Distance must be a number')

        # Check if weight_kg and distance_m have two decimal points
        if weight_kg and not (weight_kg * 100).is_integer():
            return self.fail_popup.show_popup('Failed', 'Weight must have two decimal points')
        if distance_m and not (distance_m * 100).is_integer():
            return self.fail_popup.show_popup('Failed', 'Distance must have two decimal points')

        exercise_data = {
            "exercise_name": exercise_name,
            "description": workout_description,
            "type": exercise_type,
            "body_part": body_part,
            "equipment": equipment,
            "level": exercise_level,
            "rating": '',
            "rating_description": '',
            "is_active": 1,
        }
        self.exercise.insert_exercise(exercise_data) # Inserting new exercise
        exercise_details = self.exercise.get_exercise_by_name(exercise_name)

        exercise_log_data = {
            "exercise_id": exercise_details[0][0],
            "workout_log_id": 0,
            "sets": sets,
            "reps": reps,
            "weight_kg": weight_kg,
            "rest_per_set_s": rest_s,
            "duration": duration,
            "distance_m": distance_m,
            "rpe": '',
            "is_complete": 0,
            "date_complete": '',
            "time_complete": '',
            "details": '',
            "is_active": 1,
        }
        self.exercise_log.insert_exercise_log(exercise_log_data) # Creating exercise log for the new exercise
        return self.success_popup.show_popup('Success', 'Exercise Created Successfully')

# Exercise log screen. This screen is responsible for managing exercise logs (Display/Add/Edit/Delete etc)
class ExerciseLogScreen(Screen):
    def __init__(self, **kwargs):
        super(ExerciseLogScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.exercise_log = ExerciseLog(self.local_db.connection)
        self.selected_rows = []
        self.workout_log_rows = []
    
    def switch_to_workout_history(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'workout_history_screen'
        self.clear_exercise_log_datatable_box()
        plots_screen = self.manager.get_screen('workout_history_screen')

        plots_screen.clear_workout_log_datatable_box()
        plots_screen.create_workout_log_datatable()
        self.selected_rows.clear()

    def switch_to_exercise_log_allocate(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'exercise_log_allocate_screen'
        self.clear_exercise_log_datatable_box()

        plots_screen = self.manager.get_screen('exercise_log_allocate_screen')
        plots_screen.clear_exercise_log_allocate_datatable_box()
        plots_screen.create_exercise_log_allocate_datatable()

    def clear_exercise_log_datatable_box(self):
        exercise_log_datatable_box = self.ids.exercise_log_datatable_box
        exercise_log_datatable_box.clear_widgets()

    def get_workout_log_data_from_selected_rows(self):
        self.workout_log_rows = self.manager.get_screen('workout_history_screen').get_selected_rows()
        return self.workout_log_rows[-1][0]

    # Create exercise log datatable. Contains exercise log ID, exercise name, description, sets, repitations, weight (kg), rest (sec), distance (m), rpe (difficulty) and completion status. 
    def create_exercise_log_datatable(self):
        exercise_log_datatable_box = self.ids.exercise_log_datatable_box
        exercise_log_data = self.exercise_log.get_exercise_logs_details(self.get_workout_log_data_from_selected_rows())

        if exercise_log_data:
            self.exercise_log_datatable = MDDataTable(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.95, 0.3),
                check=True,
                use_pagination=True,
                rows_num=8,
                pagination_menu_height='240dp',
                pagination_menu_pos="auto",
                background_color=[1, 0, 0, .5],
                column_data=[
                    ["Log ID", dp(25)],
                    ["Name", dp(35)],
                    ["Sets", dp(15)],
                    ["Reps", dp(15)],
                    ["Weight (kg)", dp(20)],
                    ["Rest (sec)", dp(20)],
                    ["Distance (m)", dp(20)],
                    ["RPE", dp(15)],
                    ["Complete", dp(15)]
                ],
                row_data=exercise_log_data
            )
            self.exercise_log_datatable.bind(on_check_press=self.rows_selected)
        else:
            self.exercise_log_datatable = Label(text='No Exercises Allocated', color = 'red', font_size = "20sp", bold = True) # Display error message if no exercise log found
            
        exercise_log_datatable_box.add_widget(self.exercise_log_datatable)

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = (int(row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)

    # Remove exercise log
    def remove_row(self):
        if self.selected_rows:
            for row in self.selected_rows:
                exercise_log_id = row[0]
                self.exercise_log.remove_exercise_log(row[0])
        self.clear_exercise_log_datatable_box()
        self.create_exercise_log_datatable()
        self.selected_rows.clear()

    def update_row(self):
        if self.selected_rows:
            for selected_row in self.selected_rows:
                update_popup = UpdateExerciseLogPopup(selected_row, update_exercise_log_callback=self.update_row_callback)
                update_popup.open()

    # Update exercise log
    def update_row_callback(self, exercise_log_id, sets, reps, weight, rest, distance, rpe, is_complete):
        updated_is_complete = 1 if is_complete == 'Yes' else 0
        updated_values = {
            'sets': sets,
            'reps': reps,
            'weight_kg': weight,
            'rest_per_set_s': rest,
            'distance_m': distance,
            'rpe': rpe,
            'is_complete': updated_is_complete
        }
        self.exercise_log.update_exercise_log(exercise_log_id, updated_values)
        self.clear_exercise_log_datatable_box()
        self.create_exercise_log_datatable()
        self.selected_rows.clear()
    
    def get_selected_rows(self):
        return self.selected_rows

# Exercise Log Allocate screen. This screen is responsible for allocating exercise logs to a workout log
class ExerciseLogAllocateScreen(Screen):
    def __init__(self, **kwargs):
        super(ExerciseLogAllocateScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.exercise = Exercise(self.local_db.connection)
        self.exercise_log = ExerciseLog(self.local_db.connection)
        self.workout = Workout(self.local_db.connection)
        self.workout_log = WorkoutLog(self.local_db.connection)
        self.select_workout_type = ""
        self.exercise_log_allocate_data = ""
        self.selected_rows = []
        self.exercise_log_rows = []
        self.fail_popup = FailPopup()
        self.success_popup = SuccessPopup()

    def switch_to_exercise_log(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'exercise_log_screen'
        plots_screen = self.manager.get_screen('exercise_log_screen')
        plots_screen.clear_exercise_log_datatable_box()
        plots_screen.create_exercise_log_datatable()

    def clear_exercise_log_allocate_datatable_box(self):
        exercise_log_allocate_datatable_box = self.ids.exercise_log_allocate_datatable_box
        exercise_log_allocate_datatable_box.clear_widgets()
        self.selected_rows.clear()

    def get_workout_log_id(self):
        workout_log_id = self.manager.get_screen('exercise_log_screen').get_workout_log_data_from_selected_rows()
        return workout_log_id

    # Exercise log datatable. Contains exercise log ID, exercise name, sets, repetitions, weight (kg), rest(sec), duration, and distance (m) 
    def create_exercise_log_allocate_datatable(self):
        exercise_log_allocate_datatable_box = self.ids.exercise_log_allocate_datatable_box
        self.exercise_log_allocate_data = self.exercise_log.get_all_exercise_logs_details()

        if self.exercise_log_allocate_data:
            search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, pos_hint={'center_x': 0.5})
            self.search_field = MDTextField(
                hint_text="Search",
                size_hint_x=None,
                width=300,
                pos_hint={'center_x': 0.5, 'center_y': 0.9}
            )
            # Search button for exercise logs
            self.search_button = Button(
                text="Search",
                size_hint=(None, None),
                size=(100, 50),
                pos_hint={'center_x': 0.85, 'center_y': 0.9}
            )
            self.search_button.bind(on_release=self.on_search_button_release)

            search_layout.add_widget(self.search_field)
            search_layout.add_widget(self.search_button)

            self.exercise_log_allocate_datatable = MDDataTable(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.95, 0.3),
                check=True,
                use_pagination=True,
                rows_num=8,
                pagination_menu_height='240dp',
                pagination_menu_pos="auto",
                background_color=[1, 0, 0, .5],
                column_data=[
                    ["ID", dp(25)],
                    ["Name", dp(35)],
                    ["Sets", dp(25)],
                    ["Reps", dp(25)],
                    ["Weight (kg)", dp(25)],
                    ["rest (sec)", dp(25)],
                    ["duration", dp(25)],
                    ["distance (m)", dp(25)],
                ],
                row_data=self.exercise_log_allocate_data
            )
            self.exercise_log_allocate_datatable.bind(on_check_press=self.rows_selected)

            exercise_log_allocate_datatable_box.add_widget(search_layout)
            exercise_log_allocate_datatable_box.add_widget(self.exercise_log_allocate_datatable)
            self.selected_rows.clear()
        else:
            self.exercise_log_allocate_datatable = Label(text='No Exercises Log(s) Recorded', color='red', font_size="20sp", bold=True) # Display error message if no exercise logs detected
            exercise_log_allocate_datatable_box.add_widget(self.exercise_log_allocate_datatable)

    def on_search_button_release(self, instance):
        search_query = self.search_field.text
        if search_query:
            filtered_data = [data for data in self.exercise_log_allocate_data if search_query.lower() in str(data).lower()]
            self.exercise_log_allocate_datatable.row_data = filtered_data
        else:
            self.exercise_log_allocate_datatable.row_data = self.exercise_log_allocate_data

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = ((row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)

    # Function for allocating exercise log to the selected workout log
    def allocate_log_save_button(self):
        workout_log_id = self.get_workout_log_id()
        if self.selected_rows:
            for exercise_logs in self.selected_rows:
                exercise_id = self.exercise_log.get_exercise_id(exercise_logs[0])
                exercise_log_data = {
                    'exercise_id': exercise_id,
                    'workout_log_id': workout_log_id,
                    'sets': exercise_logs[2],
                    'reps': exercise_logs[3],
                    'weight_kg': exercise_logs[4],
                    'rest_per_set_s': exercise_logs[5],
                    'duration': exercise_logs[6],
                    'distance_m': exercise_logs[7],
                    'rpe': '',
                    'is_complete': 0,
                    'date_complete': '',
                    'time_complete': '',
                    'details': '',
                    'is_active': 1, 
                }
                self.exercise_log.insert_exercise_log(exercise_log_data)
            
            return self.success_popup.show_popup('Success', 'Exercise Log(s) Allocated Successfully')
        else:
            print("No exercise log(s) selected")

# Exercise Allocate screen. This screen is responsible for allocating exercises to a workout
class ExerciseAllocateScreen(Screen):
    def __init__(self, **kwargs):
        super(ExerciseAllocateScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.exercise = Exercise(self.local_db.connection)
        self.exercise_log = ExerciseLog(self.local_db.connection)
        self.workout = Workout(self.local_db.connection)
        self.workout_log = WorkoutLog(self.local_db.connection)
        self.select_workout_type = ""
        self.exercise_allocate_data = ""
        self.selected_rows = []
        self.fail_popup = FailPopup()
        self.success_popup = SuccessPopup()

    def switch_to_workout_allocate(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'workout_allocate_screen'
        plots_screen = self.manager.get_screen('workout_allocate_screen')
        plots_screen.clear_workout_allocate_datatable_box()
        plots_screen.create_workout_allocate_datatable()

    def clear_exercise_allocate_datatable_box(self):
        exercise_allocate_datatable_box = self.ids.exercise_allocate_datatable_box
        exercise_allocate_datatable_box.clear_widgets()
        self.selected_rows.clear()

    # Exercise datatable. Contains exercise ID, exercise name, type, body part, equipment, level and rating (only for preset exercises)
    def create_exercise_allocate_datatable(self):
        self.allocate_workout_rows = self.manager.get_screen('workout_allocate_screen').get_selected_rows()        
        exercise_allocate_datatable_box = self.ids.exercise_allocate_datatable_box
        self.exercise_allocate_data = self.exercise.get_all_exercises()

        if self.exercise_allocate_data:
            search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, pos_hint={'center_x': 0.5})
            self.search_field = MDTextField(
                hint_text="Search",
                size_hint_x=None,
                width=300,
                pos_hint={'center_x': 0.5, 'center_y': 0.9}
            )

            # Search button for exercises
            self.search_button = Button(
                text="Search",
                size_hint=(None, None),
                size=(100, 50),
                pos_hint={'center_x': 0.85, 'center_y': 0.9}
            )
            self.search_button.bind(on_release=self.on_search_button_release)

            search_layout.add_widget(self.search_field)
            search_layout.add_widget(self.search_button)

            self.exercise_allocate_datatable = MDDataTable(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.95, 0.3),
                check=True,
                use_pagination=True,
                rows_num=8,
                pagination_menu_height='240dp',
                pagination_menu_pos="auto",
                background_color=[1, 0, 0, .5],
                column_data=[
                    ["ID", dp(25)],
                    ["Name", dp(35)],
                    ["Type", dp(25)],
                    ["Body Part", dp(25)],
                    ["Equipment", dp(25)],
                    ["Level", dp(25)],
                    ["Rating", dp(25)],
                ],
                row_data=self.exercise_allocate_data
            )
            self.exercise_allocate_datatable.bind(on_check_press=self.rows_selected)

            exercise_allocate_datatable_box.add_widget(search_layout)  # Add the horizontal layout
            exercise_allocate_datatable_box.add_widget(self.exercise_allocate_datatable)
            self.selected_rows.clear()
        else:
            self.exercise_allocate_datatable = Label(text='No Exercises Recorded', color='red', font_size="20sp", bold=True) # Display error message if no exercises found
            exercise_allocate_datatable_box.add_widget(self.exercise_allocate_datatable)

    def on_search_button_release(self, instance):
        search_query = self.search_field.text
        if search_query:
            filtered_data = [data for data in self.exercise_allocate_data if search_query.lower() in str(data).lower()]
            self.exercise_allocate_datatable.row_data = filtered_data
        else:
            self.exercise_allocate_datatable.row_data = self.exercise_allocate_data

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = ((row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)

    # Function for deleting exercises. Note only custom exercises made by the user can be deleted, not the preset exercises
    def remove_row(self):
        if self.selected_rows:
            for row in self.selected_rows:
                exercise_id = row[0]
                status = self.exercise.remove_exercise(exercise_id)
                self.success_popup.show_popup('Success', 'Removed custom exercise')
                if status == 0:
                    allocate_workout_success = FailPopup()
                    allocate_workout_success.show_popup('Failed', 'Cannot delete preset exercises')
        
        self.clear_exercise_allocate_datatable_box()
        self.create_exercise_allocate_datatable()

    # Function that calls the UpdateExerciseAllocatePopup class for updating exercises
    def update_row(self):
        if self.selected_rows:
            for selected_row in self.selected_rows:
                update_popup = UpdateExerciseAllocatePopup(selected_row, update_exercise_allocate_callback=self.update_row_callback)
                self.selected_rows.clear()
                update_popup.open()

    # Function that updates the exercise log
    def update_row_callback(self, exercise_id, exercise_name, description, exercise_type, body_part, equipment, level):
        workout_update = {
            'exercise_name': exercise_name,
            'description': description,
            'type': exercise_type,
            'body_part': body_part,
            'equipment': equipment,
            'level': level,
        }
        self.exercise.update_exercise(exercise_id, workout_update)
        self.clear_exercise_allocate_datatable_box()
        self.create_exercise_allocate_datatable()
        self.selected_rows.clear()

    def get_selected_rows(self):
        return self.selected_rows

    def allocate_save_button(self):
        self.allocate_workout_rows = self.manager.get_screen('workout_allocate_screen').get_selected_rows()
        if self.selected_rows: # Selected exercise
            for exercise_row in self.selected_rows:
                if exercise_row:
                    workout_log_data = self.workout_log.get_workout_logs_by_workout_id(self.allocate_workout_rows[0][0])
                    if workout_log_data: # Selected workout
                        for workout_logs in workout_log_data:
                            if workout_logs[4] == 0 and workout_logs[7] == 1:  # If selected workout is not complete and active
                                exercise_logs = self.exercise_log.get_latest_exercise_log_by_exercise_id(exercise_row[0])
                                if exercise_logs:  # If any past exercise log record exists
                                    insert_exercise_log = {
                                        'exercise_id': exercise_row[0],
                                        'workout_log_id': workout_logs[0],
                                        'sets': exercise_logs[3],
                                        'reps': exercise_logs[4],
                                        'weight_kg': exercise_logs[5],
                                        'rest_per_set_s': exercise_logs[6],
                                        'duration': exercise_logs[7],
                                        'distance_m': exercise_logs[8],
                                        'rpe': '',
                                        'is_complete': 0,
                                        'date_complete': '',
                                        'time_complete': '',
                                        'details': exercise_logs[12],
                                        'is_active': 1,
                                    }
                                    self.exercise_log.insert_exercise_log(insert_exercise_log) # Insert the latest exercise log data to the selected exercise, inside the workout
                                    self.success_popup.show_popup('Success', 'Exercise(s) Allocated Successfully')
                                else:
                                    insert_exercise_log = {
                                        'exercise_id': exercise_row[0],
                                        'workout_log_id': workout_logs[0],
                                        'sets': '',
                                        'reps': '',
                                        'weight_kg': '',
                                        'rest_per_set_s': '',
                                        'duration': '00:00:00',
                                        'distance_m': '',
                                        'rpe': '',
                                        'is_complete': 0,
                                        'date_complete': '',
                                        'time_complete': '',
                                        'details': '',
                                        'is_active': 1,
                                    }
                                    # If no exercise log record found for the selected exercise, then create a new exercise log with default values
                                    self.exercise_log.insert_exercise_log(insert_exercise_log)
                                    self.success_popup.show_popup('Success', 'Exercise(s) Allocated Successfully')
                    else:
                        new_workout_log_data = {
                            'workout_id': self.allocate_workout_rows[0][0],
                            'date_assigned': '',
                            'time_assigned': '',
                            'is_complete': 0,
                            'date_completed': '',
                            'time_completed': '',
                            'is_active': 0,
                        }

                        # If selected workout has never been used, create new workout log and fill with with default values
                        workout_log_id = self.workout_log.insert_workout_log(new_workout_log_data)
                        for exercise_row in self.selected_rows:
                            insert_exercise_log = {
                                'exercise_id': exercise_row[0],
                                'workout_log_id': workout_log_id,
                                'sets': '',
                                'reps': '',
                                'weight_kg': '',
                                'rest_per_s': '',
                                'duration': '00:00:00',
                                'distance_m': '',
                                'rpe': '',
                                'is_complete': 0,
                                'date_complete': '',
                                'time_completed': '',
                                'details': '',
                                'is_active': 1,
                            }
                            self.exercise_log.insert_exercise_log(insert_exercise_log) # Allocate the selected exercise with default values
                            self.success_popup.show_popup('Success', 'Exercise(s) Allocated Successfully')
        else:
            print("No exercise(s) selected") # Error message if no exercise selected

# Gym Finder Screen. This screen is responsible for searching for the closest gyms, user location data required to use this functionality (Incomplete)
class GymFinderScreen(Screen):
    def switch_to_dashboard(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard_screen'

    # Create map view, currently default location is set to Bristol, England.
    def create_map_view(self):
        mapview = MapView(zoom=15, lat=51.454514, lon=-2.587910)
        gym_finder_map = self.ids.gym_finder_map
        gym_finder_map.clear_widgets()
        gym_finder_map.add_widget(mapview)

    # def find_nearby_gyms(self, postcode):
    #     # Use your Google Places API key
    #     api_key = 'YOUR_GOOGLE_PLACES_API_KEY'
    #     gmaps = googlemaps.Client(key=api_key)

    #     # Geocode the provided postcode to get its coordinates
    #     geocode_result = gmaps.geocode(postcode)
    #     if not geocode_result:
    #         print(f"Could not find coordinates for the given postcode: {postcode}")
    #         return

    #     location = geocode_result[0]['geometry']['location']
    #     lat, lon = location['lat'], location['lng']

    #     # Perform a nearby search for gyms
    #     places_result = gmaps.places_nearby(
    #         location=(lat, lon),
    #         radius=1000,  # You can adjust the radius as needed
    #         type='gym'
    #     )

    #     # Extract information about nearby gyms
    #     nearby_gyms = []
    #     for place in places_result.get('results', []):
    #         name = place.get('name', 'Unknown Gym')
    #         address = place.get('vicinity', 'Unknown Address')
    #         lat = place['geometry']['location']['lat']
    #         lon = place['geometry']['location']['lng']
    #         nearby_gyms.append({'name': name, 'address': address, 'lat': lat, 'lon': lon})

    #     return nearby_gyms

# Meal History Screen. This screen is responsible for managing meal logs (Display/Add/Edit/Delete etc).
class MealHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(MealHistoryScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.meal_logs = MealLog(self.local_db.connection)
        self.selected_rows = []
        self.from_selected_date = datetime.today().strftime('%d/%m/%Y')
        from_selected_date_obj = datetime.strptime(self.from_selected_date, '%d/%m/%Y')
        self.to_selected_date_obj = from_selected_date_obj + timedelta(days=7)
        self.to_selected_date = self.to_selected_date_obj.strftime('%d/%m/%Y')

    def switch_to_dashboard(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard_screen'
        self.selected_rows.clear()
        self.clear_meal_log_datatable_box()

    def switch_to_meal_allocate(self):
        self.selected_rows.clear()
        self.manager.transition.direction = 'left'
        self.manager.current = 'meal_allocate_screen'
        self.clear_meal_log_datatable_box
        
        plots_screen = self.manager.get_screen('meal_allocate_screen')
        plots_screen.clear_meal_allocate_datatable_box()
        plots_screen.create_meal_allocate_datatable()

    def switch_to_food_item_log(self):
        if self.selected_rows:
            self.manager.transition.direction = 'left'
            self.manager.current = 'food_item_log_screen'
            plots_screen = self.manager.get_screen('food_item_log_screen')
            plots_screen.create_food_item_log_datatable()

    def clear_meal_log_datatable_box(self):
        meal_log_datatable_box = self.ids.meal_log_datatable_box
        meal_log_datatable_box.clear_widgets()
        self.selected_rows.clear()

    # From date input
    def handle_meal_log_date_from_input(self):
        if not hasattr(self, 'meal_log_date_from_date'):
            self.meal_log_date_from_date = MDDatePicker()
            self.meal_log_date_from_date.bind(on_save=self.meal_log_date_from_on_save, on_cancel=self.on_cancel)
        self.meal_log_date_from_date.open()

    # To date input
    def handle_meal_log_date_to_input(self):
        if not hasattr(self, 'meal_log_date_to_date'):
            self.meal_log_date_to_date = MDDatePicker()
            self.meal_log_date_to_date.bind(on_save=self.meal_log_date_to_on_save, on_cancel=self.on_cancel)
        self.meal_log_date_to_date.open()

    def meal_log_date_from_on_save(self, instance, value, date_range):
        screen = self.manager.get_screen('meal_history_screen')
        self.from_selected_date = value.strftime("%d/%m/%Y")
        screen.ids.meal_log_date_from.text = self.from_selected_date
        self.clear_meal_log_datatable_box()
        self.create_meal_log_datatable()

    def meal_log_date_to_on_save(self, instance, value, date_range):
        screen = self.manager.get_screen('meal_history_screen')
        self.to_selected_date = value.strftime("%d/%m/%Y")
        screen.ids.meal_log_date_to.text = self.to_selected_date
        self.clear_meal_log_datatable_box()
        self.create_meal_log_datatable()

    def on_cancel(self, instance, value):
        instance.dismiss()

    # Meal log datatable. Contains meal log ID, meal name, energy (kcal), serving portion, protein (g), fats (g), carbs (g), sugar (g), fibre (g), iron (mg), date and time assigned and completion status
    def create_meal_log_datatable(self):
        screen = self.manager.get_screen('meal_history_screen')
        screen.ids.meal_log_date_from.text = self.from_selected_date
        screen.ids.meal_log_date_to.text = self.to_selected_date
        meal_log_datatable_box = self.ids.meal_log_datatable_box
        # meal_log_data = self.meal_logs.get_meal_logs_details()
        meal_log_data = self.meal_logs.get_date_selected_meal_logs(self.from_selected_date, self.to_selected_date)

        if meal_log_data:
            self.meal_log_datatable = MDDataTable(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.95, 0.3),
                check=True,
                use_pagination=True,
                rows_num=6,
                pagination_menu_height='240dp',
                pagination_menu_pos="auto",
                background_color=[1, 0, 0, .5],
                column_data=[
                    ["Log ID", dp(25)],
                    ["Name", dp(30)],
                    ["Energy (Kcal)", dp(20)],
                    ["Protein (g)", dp(20)],
                    ["Fats (g)", dp(15)],
                    ["Carbs (g)", dp(15)],
                    ["Sugar (g)", dp(15)],
                    ["Fibre (g)", dp(15)],
                    ["Iron (mg)", dp(15)],
                    ["Date Assigned", dp(25)],
                    ["Time Assigned", dp(25)],
                    ["Complete", dp(25)]
                ],
                row_data=meal_log_data
            )
            self.meal_log_datatable.bind(on_check_press=self.rows_selected)
        else:
            self.meal_log_datatable = Label(text='No Meals Recorded', color = 'red', font_size = "20sp", bold = True) # Display error message if no meal log detected
        meal_log_datatable_box.add_widget(self.meal_log_datatable)

    def on_start_date_selected(self, instance, start_date):
        self.update_row_data(start_date, self.end_date_input.text)

    def on_end_date_selected(self, instance, end_date):
        self.update_row_data(self.start_date_input.text, end_date)

    # Function for updating meal log
    def update_row_data(self, start_date, end_date):
        row_data = self.meal_logs.get_meal_logs_details_by_date_range(start_date, end_date)
        self.meal_log_datatable.row_data = row_data

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = (int(row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)

    # Function for removing meal log
    def remove_row(self):
        if self.selected_rows:
            for row in self.selected_rows:
                meal_log_id = row[0]
                self.meal_logs.remove_meal_log(row[0])
        self.clear_meal_log_datatable_box()
        self.create_meal_log_datatable()
        self.selected_rows.clear()

    # Function for calling the UpdateMealLogPopup for updating meal log data (Incomplete)
    def update_row(self):
        if self.selected_rows:
            for selected_row in self.selected_rows:
                update_popup = UpdateMealLogPopup(selected_row, update_meal_log_callback=self.update_row_callback)
                update_popup.open()

    # Function for updating meal log data
    def update_row_callback(self, meal_log_id, date_assigned, time_assigned, is_complete):
        print("updated data", meal_log_id, date_assigned, time_assigned, is_complete)
        updated_data = {
            # 'meal_log_id': meal_log_id,
            'date_ate': date_assigned,
            'time_ate': time_assigned,
            'ate': is_complete,
        }
        if is_complete == 'Yes':
            updated_is_complete = 1
        else:
            updated_is_complete = 0

        self.meal_logs.update_meal_log(meal_log_id, updated_data)
        self.clear_meal_log_datatable_box()
        self.create_meal_log_datatable()
        self.selected_rows.clear()

    def get_selected_rows(self):
        return self.selected_rows

# Meal Allocate screen. Used for allocating meals to a selected datetime.
class MealAllocateScreen(Screen):
    def __init__(self, **kwargs):
        super(MealAllocateScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.meal = Meal(self.local_db.connection)
        self.meal_logs = MealLog(self.local_db.connection)
        self.food_item_log = FoodItemLog(self.local_db.connection)

        self.selected_rows = []
        self.selected_date = datetime.today().strftime('%d/%m/%Y')
        self.selected_time = datetime.today().strftime('%H:%M:%S')

    def switch_to_meal_history(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'meal_history_screen'
        self.clear_meal_allocate_datatable_box()
        plots_screen = self.manager.get_screen('meal_history_screen')
        plots_screen.clear_meal_log_datatable_box()
        plots_screen.create_meal_log_datatable()
        self.selected_rows.clear()

    def switch_to_meal_create(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'meal_create_screen'
        self.selected_rows.clear()
        self.clear_meal_allocate_datatable_box()

    def switch_to_food_item_create(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'food_item_create_screen'
        self.selected_rows.clear()
        self.clear_meal_allocate_datatable_box()

    # def switch_to_food_item_allocate(self):
    #     if self.selected_rows:
    #         self.manager.transition.direction = 'left'
    #         self.manager.current = 'food_item_allocate_screen'
    #         plots_screen = self.manager.get_screen('food_item_allocate_screen')
    #         plots_screen.clear_food_item_allocate_datatable_box()
    #         plots_screen.create_food_item_allocate_datatable()

    def clear_meal_allocate_datatable_box(self):
        meal_allocate_datatable_box = self.ids.meal_allocate_datatable_box
        meal_allocate_datatable_box.clear_widgets()
        self.selected_rows.clear()

    # Allocate date input
    def handle_meal_allocate_date_input(self):
        if not hasattr(self, 'meal_allocate_date'):
            self.meal_allocate_date = MDDatePicker()
            self.meal_allocate_date.bind(on_save=self.meal_allocate_date_on_save, on_cancel=self.on_cancel)
        self.meal_allocate_date.open()

    def meal_allocate_date_on_save(self, instance, value, date_range):
        screen = self.manager.get_screen('meal_allocate_screen')
        self.selected_date = value.strftime("%d/%m/%Y")
        screen.ids.meal_allocate_date.text = self.selected_date
        self.clear_meal_allocate_datatable_box()
        self.create_meal_allocate_datatable()

    def handle_meal_allocate_time_input(self):
        if not hasattr(self, 'meal_allocate_time'):
            self.meal_allocate_time = MDTimePicker()
            self.meal_allocate_time.bind(on_save=self.meal_allocate_time_on_save, on_cancel=self.on_cancel)
        self.meal_allocate_time.open()

    def meal_allocate_time_on_save(self, instance, value):
        screen = self.manager.get_screen('meal_allocate_screen')
        self.selected_time = value.strftime("%H:%M:%S")
        screen.ids.meal_allocate_time.text = self.selected_time
        self.clear_meal_allocate_datatable_box()
        self.create_meal_allocate_datatable()

    def on_cancel(self, instance, value):
        instance.dismiss()

    # Creates meal datatable and displays the meal ID, meal name, description, type and rating (for preset meals)
    def create_meal_allocate_datatable(self):
        screen = self.manager.get_screen('meal_allocate_screen')
        screen.ids.meal_allocate_date.text = self.selected_date
        screen.ids.meal_allocate_time.text = self.selected_time
        meal_allocate_datatable_box = self.ids.meal_allocate_datatable_box
        meal_allocate_data = self.meal.get_meal_details()

        if meal_allocate_data:
            self.meal_allocate_datatable = MDDataTable(
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
                    ["Type", dp(35)],
                    ["Description", dp(45)],
                ],
                row_data=meal_allocate_data
            )
            self.meal_allocate_datatable.bind(on_check_press=self.rows_selected)
        else:
            self.meal_allocate_datatable = Label(text='No Meals Recorded', color = 'red', font_size = "20sp", bold = True) # Display error message if no meals detected
            
        meal_allocate_datatable_box.add_widget(self.meal_allocate_datatable)
        self.selected_rows.clear()

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = ((row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)

    def remove_row(self):
        if self.selected_rows:
            for row in self.selected_rows:
                meal_id = row[0]
                self.meal.remove_meal(row[0])
        self.clear_meal_allocate_datatable_box()
        self.create_meal_allocate_datatable()
        self.selected_rows.clear()

    def update_row(self):
        if self.selected_rows:
            for selected_row in self.selected_rows:
                update_popup = UpdateMealAllocatePopup(selected_row, update_meal_allocate_callback=self.update_row_callback)
                self.selected_rows.clear()
                update_popup.open()

    # For updating meal stats
    def update_row_callback(self, meal_id, description, meal_type):
        meal_update = {
            'description': description,
            'type': meal_type,
        }
            
        self.meal.update_meal(meal_id, meal_update)
        self.clear_meal_allocate_datatable_box()
        self.create_meal_allocate_datatable()
        self.selected_rows.clear()

    def get_selected_rows(self):
        return self.selected_rows

    def allocate_save_button(self):
        print(self.selected_rows)
        if self.selected_rows:
            for meals in self.selected_rows:
                if not self.meal.is_meal_type_allocated(meals[1], self.selected_date):
                    # print('Meal type not allocated')
                    latest_meal_log = self.meal_logs.get_latest_meal_log_by_meal_id(meals[0][0])
                    # print(latest_meal_log)
                    meal_log_data = {}
                    if latest_meal_log:
                        meal_log_data = {
                            "meal_id": meals[0],
                            "energy_tot_kcal": latest_meal_log[0][2],
                            "protein_tot_g": latest_meal_log[0][3],
                            "lipid_tot_g":latest_meal_log[0][4],
                            "carbs_tot_g":latest_meal_log[0][5],
                            "fiber_tot_g":latest_meal_log[0][6],
                            "sugar_tot_g":latest_meal_log[0][7],
                            "calcium_tot_mg":latest_meal_log[0][8],
                            "iron_tot_mg":latest_meal_log[0][9],
                            "ate": 0,
                            "date_ate": self.selected_date,
                            "time_ate": self.selected_time,
                            "is_active": 1,
                        }
                        meal_log_id = self.meal_logs.insert_meal_log(meal_log_data)
                        latest_food_item_logs = self.food_item_log.get_food_item_by_meal_log_id(latest_meal_log[0][0])

                        for food_item_logs in latest_food_item_logs:
                            new_food_item_logs = {
                                "meal_log_id": meal_log_id,
                                "food_item_id": food_item_logs[2],
                                "serving": food_item_logs[3],
                                "weight_g": 0,
                                "ate": 0,
                                "date_ate": '',
                                "time_ate": '',
                                "description": '',
                                "is_active": 1
                            }

                            self.food_item_log.insert_food_item_log(new_food_item_logs)
                        # print('Past meal log exists, use latest one')
                    else:
                        meal_log_data = {
                            "meal_id": meals[0],
                            "energy_tot_kcal": 0,
                            "protein_tot_g": 0,
                            "lipid_tot_g":0,
                            "carbs_tot_g":0,
                            "fiber_tot_g":0,
                            "sugar_tot_g":0,
                            "calcium_tot_mg":0,
                            "iron_tot_mg":0,
                            "ate": 0,
                            "date_ate": self.selected_date,
                            "time_ate": self.selected_time,
                            "is_active": 1,
                        }
                        # print('Past meal log does not exist, create new default one')
                        self.meal_logs.insert_meal_log(meal_log_data)

                    allocate_meal_success = SuccessPopup()
                    allocate_meal_success.show_popup('Success', 'Meal Allocated!')
                    # print('inserted meal log')

                else:
                    allocate_meal_fail = FailPopup()
                    allocate_meal_fail.show_popup('Failed', f"{meals[1]} has already been\nallocated on this date!")
                    # print('meal type already exists for selected date')

    def get_selected_rows(self):
        return self.selected_rows

# Meal Create screen. This screen is responsible for creating a new meal.
class MealCreateScreen(Screen):
    def __init__(self, **kwargs):
        super(MealCreateScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.meal = Meal(self.local_db.connection)
        self.select_meal_type = ""
        self.fail_popup = FailPopup()
        self.success_popup = SuccessPopup()

    def switch_to_meal_allocate(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'meal_allocate_screen'
        plots_screen = self.manager.get_screen('meal_allocate_screen')
        plots_screen.clear_meal_allocate_datatable_box()
        plots_screen.create_meal_allocate_datatable()

    def handle_meal_description_input(self, text):
        self.ids.meal_description_input.error = not text

    def show_meal_type_menu(self, instance):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Breakfast", "on_release": lambda x="Breakfast": self.set_selected_meal_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Morning Snack", "on_release": lambda x="Morning Snack": self.set_selected_meal_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Lunch", "on_release": lambda x="Lunch": self.set_selected_meal_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Brunch", "on_release": lambda x="Brunch": self.set_selected_meal_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Afternoon Snack", "on_release": lambda x="Afternoon Snack": self.set_selected_meal_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Dinner", "on_release": lambda x="Dinner": self.set_selected_meal_type(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Evening Snack", "on_release": lambda x="Evening Snack": self.set_selected_meal_type(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def set_selected_meal_type(self, selected_meal_type_text, textfield_instance):
        self.ids.meal_type_input.text = selected_meal_type_text

    def verify_meal_create_input(self):
        meal_type = self.ids.meal_type_input.text
        meal_description = self.ids.meal_description_input.text

        if not meal_description:
            return self.fail_popup.show_popup('Failed', 'Enter Meal Name')
        if not meal_type:
            return self.fail_popup.show_popup('Failed', 'Select Meal Type')

        meal_data = {
            "type": meal_type,
            "description": meal_description,
            "date_created": datetime.now().strftime("%d/%m/%Y"),
            "time_created":datetime.now().strftime('%H:%M:%S'), 
            "is_active": 1
        }
        self.meal.insert_meal(meal_data)
        return self.success_popup.show_popup('Success', 'Meal Created Successfully')

# Food Item Create screen. This screen is responsible for creating a new food item
class FoodItemCreateScreen(Screen):
    def __init__(self, **kwargs):
        super(FoodItemCreateScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.food_item = FoodItem(self.local_db.connection)
        self.food_item_log = FoodItemLog(self.local_db.connection)
        self.select_meal_type = ""
        self.fail_popup = FailPopup()
        self.success_popup = SuccessPopup()

    def switch_to_meal_allocate(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'meal_allocate_screen'
        plots_screen = self.manager.get_screen('meal_allocate_screen')
        plots_screen.clear_meal_allocate_datatable_box()
        plots_screen.create_meal_allocate_datatable()

    def handle_food_item_name_input(self, text):
        self.ids.food_item_name_input.error = not text

    # Verify food_item input data
    def verify_food_item_create_input(self):
        food_item_name = self.ids.food_item_name_input.text
        energy_kcal = self.ids.food_item_energy_kcal.text
        protein_g = self.ids.protein_g_input.text
        lipid_g = self.ids.lipid_g_input.text
        carbs_g = self.ids.carbs_g_input.text
        fibre_td_g = self.ids.fibre_td_input.text
        sugar_g = self.ids.sugar_g_input.text
        calcium_mg = self.ids.calcium_mg_input.text
        iron_mg = self.ids.iron_mg_input.text
        cholestrol_mg = self.ids.cholestrol_mg_input.text


        if not food_item_name:
            return self.fail_popup.show_popup('Failed', 'Enter Food Item name')
        if not energy_kcal:
            return self.fail_popup.show_popup('Failed', 'Enter Total Calories')
        if energy_kcal:
            try:
                energy_kcal = int(energy_kcal)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Energy (kcal) must be an integer')
        if protein_g:
            try:
                protein_g = float(protein_g)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Protein (g) must be a number')
        if lipid_g:
            try:
                lipid_g = float(lipid_g)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Fats (g) must be a number')
        if carbs_g:
            try:
                carbs_g = float(carbs_g)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Carbohydrates (g) must be a number')
        if fibre_td_g:
            try:
                fibre_td_g = float(fibre_td_g)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Fibre (g) must be a number')
        if sugar_g:
            try:
                sugar_g = float(sugar_g)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Sugar (g) must be a number')
        if calcium_mg:
            try:
                calcium_mg = float(calcium_mg)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Calcium (mg) must be a number')
        if iron_mg:
            try:
                iron_mg = float(iron_mg)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Iron (mg) must be a number')
        if cholestrol_mg:
            try:
                cholestrol_mg = float(cholestrol_mg)
            except ValueError:
                return self.fail_popup.show_popup('Failed', 'Cholestrol (mg) must be a number')

        food_item_data = {
            "food_item_name": food_item_name,
            "water_g": 0,
            "energy_kcal": energy_kcal,
            "protein_g": protein_g,
            "lipid_g": lipid_g,
            "carbs_g": carbs_g,
            "fiber_td_g": fibre_td_g,
            "sugar_g": sugar_g,
            "calcium_mg": calcium_mg,
            "iron_mg": iron_mg,
            "cholestrl_mg": cholestrol_mg,
            "gmwt_1": 0,
            "gmwt_desc1": '',
            "gmwt_2": 0,
            "gmwt_desc2": '',
            "is_active": 1,
        }
        self.food_item.insert_food_item(food_item_data) # Inserting new food item
        food_item_details = self.food_item.get_food_item_by_name(food_item_name)
        print(food_item_details)
        print(food_item_details[0][0])

        food_item_log_data = {
            "food_item_id": food_item_details[0][0],
            "meal_log_id": 0,
            "serving": 1,
            "weight_g": '',
            "ate": 0,
            "date_ate": '',
            "time_ate": '',
            "description": '',
            "is_active": 1,
        }
        self.food_item_log.insert_food_item_log(food_item_log_data) # Creating food_item log for the new food_item
        return self.success_popup.show_popup('Success', 'Food Item Created Successfully')

# Food Item log screen. This screen is responsible for managing food item logs (Display/Add/Edit/Delete etc).
class FoodItemLogScreen(Screen):
    def __init__(self, **kwargs):
        super(FoodItemLogScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.food_item_log = FoodItemLog(self.local_db.connection)
        self.meal_log = MealLog(self.local_db.connection)
        self.selected_rows = []
        self.meal_log_rows = []
    
    def switch_to_meal_history(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'meal_history_screen'
        self.clear_food_item_log_datatable_box()
        plots_screen = self.manager.get_screen('meal_history_screen')

        plots_screen.clear_meal_log_datatable_box()
        plots_screen.create_meal_log_datatable()
        self.selected_rows.clear()

    def switch_to_food_item_log_allocate(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'food_item_log_allocate_screen'
        self.clear_food_item_log_datatable_box()
        plots_screen = self.manager.get_screen('food_item_log_allocate_screen')
        plots_screen.clear_food_item_log_allocate_datatable_box()
        plots_screen.create_food_item_log_allocate_datatable()

    def clear_food_item_log_datatable_box(self):
        food_item_log_datatable_box = self.ids.food_item_log_datatable_box
        food_item_log_datatable_box.clear_widgets()

    def get_meal_log_data_from_selected_rows(self):
        self.meal_log_rows = self.manager.get_screen('meal_history_screen').get_selected_rows()
        return self.meal_log_rows[-1][0]

    # Create food_item log datatable. Contains food_item log ID, food_item name, description, sets, repitations, weight (kg), rest (sec), distance (m), rpe (difficulty) and completion status. 
    def create_food_item_log_datatable(self):
        food_item_log_datatable_box = self.ids.food_item_log_datatable_box
        food_item_log_data = self.food_item_log.get_food_item_logs_details(self.get_meal_log_data_from_selected_rows())

        if food_item_log_data:
            self.food_item_log_datatable = MDDataTable(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.95, 0.3),
                check=True,
                use_pagination=True,
                rows_num=8,
                pagination_menu_height='240dp',
                pagination_menu_pos="auto",
                background_color=[1, 0, 0, .5],
                column_data=[
                    ["Log ID", dp(25)],
                    ["Name", dp(45)],
                    ["Serving", dp(15)],
                    ["Energy (kcal)", dp(20)],
                    ["protein (g)", dp(20)],
                    ["Fats (g)", dp(15)],
                    ["Carbs (g)", dp(15)],
                    ["Sugar (g)", dp(15)],
                    ["Fibre (g)", dp(15)],
                    ["Iron (mg)", dp(15)],
                    ["Complete", dp(25)]
                ],
                row_data=food_item_log_data
            )
            self.food_item_log_datatable.bind(on_check_press=self.rows_selected)
        else:
            self.food_item_log_datatable = Label(text='No Food Items Allocated', color = 'red', font_size = "20sp", bold = True) # Display error message if no food_item log found
            
        food_item_log_datatable_box.add_widget(self.food_item_log_datatable)

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = (int(row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)

    # Remove food_item log
    def remove_row(self):
        if self.selected_rows:
            for row in self.selected_rows:
                food_item_log_id = row[0]
                self.food_item_log.remove_food_item_log(row[0])
        self.clear_food_item_log_datatable_box()
        self.create_food_item_log_datatable()
        self.selected_rows.clear()

    def update_row(self):
        if self.selected_rows:
            for selected_row in self.selected_rows:
                update_popup = UpdateFoodItemLogPopup(selected_row, update_food_item_log_callback=self.update_row_callback)
                update_popup.open()

    # Update food_item log
    def update_row_callback(self, food_item_log_id, serving, is_complete):
        updated_is_complete = 1 if is_complete == 'Yes' else 0
        updated_values = {
            'serving': serving,
            'ate': updated_is_complete
        }
        self.food_item_log.update_food_item_log(food_item_log_id, updated_values)

        updated_meal_log = self.meal_log.calculate_nutrients(self.get_meal_log_data_from_selected_rows())
        self.meal_log.update_meal_log(self.get_meal_log_data_from_selected_rows(), updated_meal_log)


        self.clear_food_item_log_datatable_box()
        self.create_food_item_log_datatable()
        self.selected_rows.clear()
    
    def get_selected_rows(self):
        return self.selected_rows

# Food Item Allocate screen. This screen is responsible for allocating food item logs to a meal log.
class FoodItemLogAllocateScreen(Screen):
    def __init__(self, **kwargs):
        super(FoodItemLogAllocateScreen, self).__init__(**kwargs)
        self.local_db = LocalDB('local_db.db')
        self.food_item = FoodItem(self.local_db.connection)
        self.food_item_log = FoodItemLog(self.local_db.connection)
        self.meal = Meal(self.local_db.connection)
        self.meal_log = MealLog(self.local_db.connection)
        self.select_meal_type = ""
        self.food_item_log_allocate_data = ""
        self.selected_rows = []
        self.food_item_log_rows = []
        self.fail_popup = FailPopup()
        self.success_popup = SuccessPopup()

    def switch_to_food_item_log(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'food_item_log_screen'
        plots_screen = self.manager.get_screen('food_item_log_screen')
        plots_screen.clear_food_item_log_datatable_box()
        plots_screen.create_food_item_log_datatable()

    def clear_food_item_log_allocate_datatable_box(self):
        food_item_log_allocate_datatable_box = self.ids.food_item_log_allocate_datatable_box
        food_item_log_allocate_datatable_box.clear_widgets()
        self.selected_rows.clear()

    def get_meal_log_id(self):
        meal_log_id = self.manager.get_screen('food_item_log_screen').get_meal_log_data_from_selected_rows()
        return meal_log_id

    # food_item log datatable. Contains food_item log ID, food_item name, sets, repetitions, weight (kg), rest(sec), duration, and distance (m) 
    def create_food_item_log_allocate_datatable(self):
        food_item_log_allocate_datatable_box = self.ids.food_item_log_allocate_datatable_box
        self.food_item_log_allocate_data = self.food_item_log.get_all_food_item_logs_details()

        if self.food_item_log_allocate_data:
            search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, pos_hint={'center_x': 0.5})
            self.search_field = MDTextField(
                hint_text="Search",
                size_hint_x=None,
                width=300,
                pos_hint={'center_x': 0.5, 'center_y': 0.9}
            )
            # Search button for food_item logs
            self.search_button = Button(
                text="Search",
                size_hint=(None, None),
                size=(100, 50),
                pos_hint={'center_x': 0.85, 'center_y': 0.9}
            )
            self.search_button.bind(on_release=self.on_search_button_release)

            search_layout.add_widget(self.search_field)
            search_layout.add_widget(self.search_button)

            self.food_item_log_allocate_datatable = MDDataTable(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.95, 0.3),
                check=True,
                use_pagination=True,
                rows_num=8,
                pagination_menu_height='240dp',
                pagination_menu_pos="auto",
                background_color=[1, 0, 0, .5],
                column_data=[
                    ["Log ID", dp(25)],
                    ["Name", dp(45)],
                    ["Serving", dp(15)],
                    ["Energy (kcal)", dp(20)],
                    ["protein (g)", dp(20)],
                    ["Fats (g)", dp(15)],
                    ["Carbs (g)", dp(15)],
                    ["Sugar (g)", dp(15)],
                    ["Fibre (g)", dp(15)],
                    ["Iron (mg)", dp(15)]
                ],
                row_data=self.food_item_log_allocate_data
            )
            self.food_item_log_allocate_datatable.bind(on_check_press=self.rows_selected)

            food_item_log_allocate_datatable_box.add_widget(search_layout)
            food_item_log_allocate_datatable_box.add_widget(self.food_item_log_allocate_datatable)
            self.selected_rows.clear()
        else:
            self.food_item_log_allocate_datatable = Label(text='No Food Items Log(s) Recorded', color='red', font_size="20sp", bold=True) # Display error message if no food_item logs detected
            food_item_log_allocate_datatable_box.add_widget(self.food_item_log_allocate_datatable)

    def on_search_button_release(self, instance):
        search_query = self.search_field.text
        if search_query:
            filtered_data = [data for data in self.food_item_log_allocate_data if search_query.lower() in str(data).lower()]
            self.food_item_log_allocate_datatable.row_data = filtered_data
        else:
            self.food_item_log_allocate_datatable.row_data = self.food_item_log_allocate_data

    def rows_selected(self, instance_table, current_row):
        row_data = tuple(current_row)
        modified_row_data = ((row_data[0]),) + row_data[1:]
        if modified_row_data in self.selected_rows:
            self.selected_rows.remove(modified_row_data)
        else:
            self.selected_rows.append(modified_row_data)

    # Function for allocating food_item log to the selected meal log
    def allocate_log_save_button(self):
        meal_log_id = self.get_meal_log_id()
        if self.selected_rows:
            for food_item_logs in self.selected_rows:
                food_item_id = self.food_item_log.get_food_item_id(food_item_logs[0])
                food_item_log_data = {
                    'meal_log_id': meal_log_id,
                    'food_item_id': food_item_id,
                    'serving': food_item_logs[2],
                    'weight_g': '',
                    'ate': 0,
                    'date_ate': '',
                    'time_ate': '',
                    'description': '',
                    'is_active': 1, 
                }
                self.food_item_log.insert_food_item_log(food_item_log_data)
            
            return self.success_popup.show_popup('Success', 'Food Item Log(s) Allocated Successfully')
        else:
            print("No Food Item log(s) selected")

# Food Item Allocate screen. This screen is responsible for allocating food items to a meal (Incomplete)
class FoodItemAllocateScreen(Screen):
    pass

""" 
Body Statistics screen. This screen is used for managing body stats data (Display/Add/Edit/Delete etc). Delete data functionality has not been fully implemented as of now (Partically Incomplete).
This screen contains an input form, where the user can manually enter weight (kg), height (cm), body fat (kg), skeletal muscle mass (kg) and step data. Only date and weight are required fields.
Also note that user does not need to enter body fat and BMI, this is automatically calculated using the user's gender, latest height and weight inputs.
"""
class BodyStatsScreen(Screen):
    def switch_to_dashboard(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard_screen'

    # Select what type of body data graph to view
    def switch_to_body_stats_plots(self, button_instance, button_value):
        selected_month = self.ids.month.text
        selected_year = self.ids.year.text
        plots_screen = self.manager.get_screen('body_stats_plots_screen')

        if button_value == 'weight':
            plots_screen.plot_monthly_weight(selected_month, selected_year)
            plots_screen.plot_yearly_weight(selected_year)
        elif button_value == 'bmi':
            plots_screen.plot_monthly_bmi(selected_month, selected_year)
            plots_screen.plot_yearly_bmi(selected_year)
        elif button_value == 'body_fat':
            plots_screen.plot_monthly_body_fat(selected_month, selected_year)
            plots_screen.plot_yearly_body_fat(selected_year)
        elif button_value == 'skeletal_muscle':
            plots_screen.plot_monthly_skeletal_muscle(selected_month, selected_year)
            plots_screen.plot_yearly_skeletal_muscle(selected_year)
        elif button_value == 'step_count':
            plots_screen.plot_monthly_step_count(selected_month, selected_year)
            plots_screen.plot_yearly_step_count(selected_year)

        self.manager.transition.direction = 'left'
        self.manager.current = 'body_stats_plots_screen'

"""
Body Statistics Plots screen. This screen is used for viewing the selected body stat data using plots. The graphs can be generated using the selected month and year inputs in the `BodyStatsScreen`.

The user can generate monthly and yearly graphs of the following body data:
Weight, BMI, body fat, skeletal muscle, and steps.
"""
class BodyStatsPlotsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def switch_to_body_stats(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'body_stats_screen'

    def plot_monthly_weight(self, selected_month, selected_year):
        local_db = LocalDB('local_db.db')
        weight = Weight(local_db.connection)
        try:
            box2 = self.ids.box2
            fig2, ax3 = plt.subplots()
            canvas = fig2.canvas
            weight_data = weight.monthly_weight_data(selected_month, selected_year)
            plt.plot(weight_data[0], weight_data[1], color='brown', alpha=0.7)
            plt.xlabel('Day of the Month')
            plt.ylabel('Weight (kg)')
            plt.title(f'Monthly Weight for {selected_month}/{selected_year}')
            plt.xticks(weight_data[2])
            plt.grid(axis='y')
            plt.axhline(y=75, color='r', linestyle='--')
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
        
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_yearly_weight(self, selected_year):
        local_db = LocalDB('local_db.db')
        weight = Weight(local_db.connection)
        try:
            box2 = self.ids.box2
            fig3, ax3 = plt.subplots()
            canvas = fig3.canvas
            weight_data = weight.yearly_weight_data(selected_year)
            plt.bar(weight_data[0], weight_data[1], color='brown')
            plt.axhline(y=75, color='r', linestyle='--')
            plt.xlabel('Month')
            plt.ylabel('Average Weight (kg)')
            plt.title(f'Yearly Average Weight for {selected_year}')
            plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            plt.grid(axis='y')
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
            
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_monthly_bmi(self, selected_month, selected_year):
        local_db = LocalDB('local_db.db')
        bmi = BMI(local_db.connection)
        try:
            box2 = self.ids.box2
            fig, ax = plt.subplots()
            canvas = fig.canvas
            bmi_data = bmi.monthly_bmi_data(int(selected_month), int(selected_year))

            bmi_ranges = [18.5, 24.9, 29.9, 39.9, 52]
            colors = ['blue', 'lightblue', 'yellow', 'red', 'darkred']
            labels = ['Underweight', 'Healthy', 'Overweight', 'Obese', 'Morbidly Obese']

            for i in range(len(bmi_ranges)):
                plt.axhspan(bmi_ranges[i-1] if i > 0 else 0, bmi_ranges[i], color=colors[i], alpha=0.5)
            plt.plot(bmi_data[0], bmi_data[1], color='black', alpha=0.7)
            plt.title(f'Monthly BMI for {selected_month}/{selected_year}')
            plt.xlabel('Day of the Month')
            plt.xticks(bmi_data[2])
            plt.grid(axis='y')
            tick_labels = [f'{label} {value}' for label, value in zip(labels, bmi_ranges)]
            plt.yticks(bmi_ranges, tick_labels)
            plt.tight_layout()
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
        
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_yearly_bmi(self, selected_year):
        local_db = LocalDB('local_db.db')
        bmi = BMI(local_db.connection)
        
        try:
            box2 = self.ids.box2
            fig, ax = plt.subplots()
            canvas = fig.canvas
            bmi_data = bmi.yearly_bmi_data(int(selected_year))

            bmi_ranges = [18.5, 24.9, 29.9, 39.9, 52]
            colors = ['blue', 'lightblue', 'yellow', 'red', 'darkred']
            labels = ['Underweight', 'Healthy', 'Overweight', 'Obese', 'Morbidly Obese']

            for i in range(len(bmi_ranges)):
                plt.axhspan(bmi_ranges[i-1] if i > 0 else 0, bmi_ranges[i], color=colors[i], alpha=0.5)
            plt.plot(bmi_data[0], bmi_data[1], color='black', marker='o')
            plt.title(f'Yearly Average BMI for {selected_year}')
            plt.xlabel('Month')
            plt.xticks(bmi_data[0], bmi_data[2])
            plt.grid(True)
            tick_labels = [f'{label} {value}' for label, value in zip(labels, bmi_ranges)]
            plt.yticks(bmi_ranges, tick_labels)
            plt.tight_layout()
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
        
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_monthly_body_fat(self, selected_month, selected_year):
        local_db = LocalDB('local_db.db')
        body_fat = BodyFat(local_db.connection)
        user = User()
        gender = user.get_user_gender(logged_user)
        try:
            box2 = self.ids.box2
            fig5, ax5 = plt.subplots()
            canvas = fig5.canvas
            body_fat_data = body_fat.monthly_body_fat_data(int(selected_month), int(selected_year))

            if gender == 'Male':
                body_fat_ranges = [5, 10, 14, 20, 24, 50]
            elif gender == 'Female':
                body_fat_ranges = [8, 15, 23, 30, 36, 50]

            colors = ['gray', 'blue', 'lightblue', 'yellow', 'red', 'darkred']
            labels = ['Dangerously Low', 'Athletic', 'Fit', 'Average', 'Overweight', 'Obese']

            for i in range(len(body_fat_ranges)):
                plt.axhspan(body_fat_ranges[i-1] if i > 0 else 0, body_fat_ranges[i], color=colors[i], alpha=0.5)
            plt.plot(body_fat_data[0], body_fat_data[1], color='black', alpha=0.7)
            plt.title(f'Monthly Body Fat % for {selected_month}/{selected_year}')
            plt.xlabel('Day of the Month')
            plt.ylabel('Body Fat (%)')
            plt.xticks(body_fat_data[2])
            plt.grid(axis='y')
            tick_labels = [f'{label} {value}' for label, value in zip(labels, body_fat_ranges)]
            plt.yticks(body_fat_ranges, tick_labels)
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
        
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_yearly_body_fat(self, selected_year):
        local_db = LocalDB('local_db.db')
        body_fat = BodyFat(local_db.connection)
        user = User()
        gender = user.get_user_gender(logged_user)
        try:
            box2 = self.ids.box2
            fig6, ax6 = plt.subplots()
            canvas = fig6.canvas
            body_fat_data = body_fat.yearly_body_fat_data(int(selected_year))

            if gender == 'Male':
                body_fat_ranges = [5, 10, 14, 20, 24, 50]
            elif gender == 'Female':
                body_fat_ranges = [8, 15, 23, 30, 36, 50]

            colors = ['gray', 'blue', 'lightblue', 'yellow', 'red', 'darkred']
            labels = ['Dangerous', 'Athletic', 'Fit', 'Average', 'Overweight', 'Obese']

            for i in range(len(body_fat_ranges)):
                plt.axhspan(body_fat_ranges[i-1] if i > 0 else 0, body_fat_ranges[i], color=colors[i], alpha=0.5)

            plt.plot(body_fat_data[0], body_fat_data[1], color='black', marker='o')
            plt.title(f'Yearly Average Body Fat % for {selected_year}')
            plt.xlabel('Month')
            plt.xticks(body_fat_data[0], body_fat_data[2])
            plt.grid(True)
            tick_labels = [f'{label} {value}' for label, value in zip(labels, body_fat_ranges)]
            plt.yticks(body_fat_ranges, tick_labels)
            plt.tight_layout()
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
        
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_monthly_skeletal_muscle(self, selected_month, selected_year):
        local_db = LocalDB('local_db.db')
        skeletal_muscle = SkeletalMuscle(local_db.connection)
        try:
            box2 = self.ids.box2
            fig7, ax7 = plt.subplots()
            canvas = fig7.canvas
            skeletal_muscle_data = skeletal_muscle.monthly_skeletal_muscle_data((selected_month), selected_year)
            plt.plot(skeletal_muscle_data[0], skeletal_muscle_data[1], color='brown', alpha=0.7)
            plt.xlabel('Day of the Month')
            plt.ylabel('Skeletal Muscle (kg)')
            plt.title(f'Monthly Skeletal Muscle for {selected_month}/{selected_year}')
            plt.xticks(skeletal_muscle_data[2])
            plt.grid(axis='y')
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
        
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_yearly_skeletal_muscle(self, selected_year):
        local_db = LocalDB('local_db.db')
        skeletal_muscle = SkeletalMuscle(local_db.connection)
        try:
            box2 = self.ids.box2
            fig8, ax8 = plt.subplots()
            canvas = fig8.canvas
            skeletal_muscle_data = skeletal_muscle.yearly_skeletal_muscle_data(selected_year)
            plt.bar(skeletal_muscle_data[0], skeletal_muscle_data[1], color='brown')
            plt.xlabel('Month')
            plt.ylabel('Average Skeletal Muscle (kg)')
            plt.title(f'Yearly Average Skeletal Muscle for {selected_year}')
            plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            plt.grid(axis='y')
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
            
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_monthly_step_count(self, selected_month, selected_year):
        local_db = LocalDB('local_db.db')
        step_count = StepCount(local_db.connection)
        try:
            box2 = self.ids.box2
            fig2, ax3 = plt.subplots()
            canvas = fig2.canvas
            step_count_data = step_count.monthy_step_count_data(selected_month, selected_year)
            plt.plot(step_count_data[0], step_count_data[1], color='brown', alpha=0.7)
            plt.xlabel('Day of the Month')
            plt.ylabel('Skeps Taken')
            plt.title(f'Monthly Steps Taken for {selected_month}/{selected_year}')
            plt.xticks(step_count_data[2])
            plt.grid(axis='y')
            plt.axhline(y=6000, color='r', linestyle='--')
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
        
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_yearly_step_count(self, selected_year):
        local_db = LocalDB('local_db.db')
        step_count = StepCount(local_db.connection)
        try:
            box2 = self.ids.box2
            fig3, ax3 = plt.subplots()
            canvas = fig3.canvas
            step_count_data = step_count.yearly_step_count_data(selected_year)
            plt.bar(step_count_data[0], step_count_data[1], color='brown')
            plt.axhline(y=6000, color='r', linestyle='--')
            plt.xlabel('Month')
            plt.ylabel('Average Skeps Taken')
            plt.title(f'Yearly Average Steps Taken for {selected_year}')
            plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            plt.grid(axis='y')
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box2.add_widget(canvas)
            
        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

"""
Water Intake Screen. This function contains a form where the user can manually input water drank (per day) in millimetres (ml). User can also modify and delete (all records) water data.
Users can also generate water intake graphs (monthly and annually) by inputing the selected month and year.
"""
class WaterIntakeScreen(Screen):
    def switch_to_dashboard(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard_screen'

    def switch_to_water_intake_plots(self):
        selected_month = self.ids.month.text
        selected_year = self.ids.year.text
        plots_screen = self.manager.get_screen('water_intake_plots_screen')
        plots_screen.plot_monthly_water_intake(selected_month, selected_year)
        plots_screen.plot_yearly_water_intake(selected_year)
        self.manager.transition.direction = 'left'
        self.manager.current = 'water_intake_plots_screen'

# Water Intake Plots Screen. This screen is used for viewing the water intake data using plots. The graphs can be generated using the selected month and year inputs in the `WaterIntakeScreen`. 
class WaterIntakePlotsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def switch_to_water_intake(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'water_intake_screen'

    def plot_monthly_water_intake(self, selected_month, selected_year):
        local_db = LocalDB('local_db.db')
        water_intake = WaterIntake(local_db.connection)
        try:
            box1 = self.ids.box1
            fig, ax = plt.subplots(figsize=(250, 150))
            canvas = fig.canvas
            water_intake_data = water_intake.monthly_water_intake_data(selected_month, selected_year)
            plt.bar(water_intake_data[0], water_intake_data[1], color='b', alpha=0.7)
            plt.title(f'Monthly Water Intake for {selected_month}/{selected_year}')
            plt.xlabel('Day of the Month')
            plt.ylabel('Water Intake (ml)')
            plt.axhline(y=2000, color='r', linestyle='--')
            plt.xticks(water_intake_data[2])
            plt.grid(axis='y')
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box1.add_widget(canvas)

        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

    def plot_yearly_water_intake(self, selected_year):
        local_db = LocalDB('local_db.db')
        water_intake = WaterIntake(local_db.connection)
        try:
            box1 = self.ids.box1
            fig1, ax1 = plt.subplots()
            canvas = fig1.canvas
            water_intake_data = water_intake.yearly_water_intake_graph(selected_year)
            plt.figure(figsize=(12, 8))
            plt.bar(water_intake_data[0], water_intake_data[1], color='b', alpha=0.7)
            plt.xlabel('Month')
            plt.ylabel('Average Water Intake (ml)')
            plt.title(f'Yearly Average Water Intake for {selected_year}')
            plt.xticks(range(1, 13))
            plt.grid(axis='y')
            plt.axhline(y=2000, color='r', linestyle='--')
            canvas = FigureCanvasKivyAgg(plt.gcf())
            box1.add_widget(canvas)

        except Exception as e:
            print("Error:", e)
        finally:
            local_db.close_connection()

"""
Arduino Watch screen. This screen is used for synching with the Arduino Watch via Bluetooth LE. All the Arduino Watch data should be transferred to the LocalDB Database. (Incomplete)
After the data from the Arduino Watch is synched, the user can choose to generate graphs on the data gathered by the Arduino Watch.
"""
class ArduinoWatchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def switch_to_dashboard(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard_screen'

    # User can choose which data from the Arduino Watch to create a graph of
    def switch_to_arduino_watch_plots(self, button_instance, button_value):
        plots_screen = self.manager.get_screen('arduino_watch_plots_screen')
        if button_value == 'heart_rate':
            plots_screen.plot_heart_rate()
        elif button_value == 'blood_oxygen_level':
            plots_screen.plot_oxygen_level()
        elif button_value == 'step_count':
            plots_screen.plot_step_count()
        elif button_value == 'body_temperature':
            plots_screen.plot_body_temperature()
        self.manager.transition.direction = 'left'
        plots_screen = self.manager.current = 'arduino_watch_plots_screen'

"""
Arduino Watch Plots screen. This screen is used for viewing the selected body stat data using plots from the Arduino Watch. (Incomplete)

The user can generate graphs of the following body data:
Heart Rate, Blood Oxygen Level, Step Count, and Body Temperature.
"""
class ArduinoWatchPlotsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arduino_watch = ArduinoWatch()

    def switch_to_dashboard(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard_screen'

    def switch_to_arduino_watch(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'arduino_watch_screen'

    def plot_heart_rate(self):
        try:
            heart_rate_data = self.arduino_watch.heart_rate_data()
            box2 = self.ids.box2
            box2.clear_widgets()

            if not heart_rate_data:
                return box2.add_widget(Label(text='No Heart Rate Data Detected.', color = 'red', font_size = "20sp", bold = True))
            epoch_times = [int(entry[0]) for entry in heart_rate_data]
            heart_rates = [entry[1] for entry in heart_rate_data]
            start_time = epoch_times[0]
            normalized_times = [time - start_time for time in epoch_times]
            fig, ax = plt.subplots()
            ax.plot(normalized_times, heart_rates, color='red', alpha=0.7)
            ax.set_xlabel('Seconds')
            ax.set_ylabel('Heart Rate (bpm)')
            ax.set_title('Heart Rate')
            ax.grid(axis='y')
            ax.yaxis.set_major_locator(MultipleLocator(10))
            canvas = FigureCanvasKivyAgg(fig)
            box2.add_widget(canvas)

        except Exception as e:
            print("Error:", e)

    def plot_oxygen_level(self):
        try:
            oxygen_level_data = self.arduino_watch.oxygen_level_data()
            box2 = self.ids.box2
            box2.clear_widgets()

            if not oxygen_level_data:
                return box2.add_widget(Label(text='No Blood Oxygen Data Detected.', color = 'red', font_size = "20sp", bold = True))
            epoch_times = [int(entry[0]) for entry in oxygen_level_data]
            oxygen_levels = [entry[1] for entry in oxygen_level_data]

            start_time = epoch_times[0]
            normalized_times = [time - start_time for time in epoch_times]
            fig, ax = plt.subplots()
            bar_width = 1
            ax.bar(normalized_times, oxygen_levels, width=bar_width, color='red', alpha=0.7)
            ax.set_xlabel('Seconds')
            ax.set_ylabel('Blood Oxygen %')
            ax.set_title('Blood Oxygen (Percent)')
            ax.grid(axis='y')
            ax.yaxis.set_major_locator(MultipleLocator(5))
            ax.set_ylim(bottom=75)
            canvas = FigureCanvasKivyAgg(fig)
            box2.add_widget(canvas)

        except Exception as e:
            print("Error:", e)

    def plot_step_count(self):
        try:
            step_count_data = self.arduino_watch.step_count_data()
            box2 = self.ids.box2
            box2.clear_widgets()

            if not step_count_data:
                return box2.add_widget(Label(text='No Step Data Detected.', color = 'red', font_size = "20sp", bold = True))
            epoch_times = [int(entry[0]) for entry in step_count_data]
            step_counts = [entry[1] for entry in step_count_data]
            start_time = epoch_times[0]
            normalized_times = [time - start_time for time in epoch_times]
            fig, ax = plt.subplots()
            bar_width = 1
            ax.bar(normalized_times, step_counts, width=bar_width, color='brown', alpha=0.7)
            ax.set_xlabel('Seconds')
            ax.set_ylabel('Total Steps')
            ax.set_title('Step Count')
            ax.grid(axis='y')
            ax.yaxis.set_major_locator(MultipleLocator(10))
            ax.set_ylim(bottom=0)
            canvas = FigureCanvasKivyAgg(fig)
            box2.add_widget(canvas)

        except Exception as e:
            print("Error:", e)

    def plot_body_temperature(self):
        try:
            body_temperature_data = self.arduino_watch.body_temperature_data()
            box2 = self.ids.box2
            box2.clear_widgets()

            if not body_temperature_data:
                return box2.add_widget(Label(text='No Body Temperature Data Detected.', color = 'red', font_size = "20sp", bold = True))
            epoch_times = [int(entry[0]) for entry in body_temperature_data]
            body_temperatures = [entry[1] for entry in body_temperature_data]
            start_time = epoch_times[0]
            normalized_times = [time - start_time for time in epoch_times]
            fig, ax = plt.subplots()
            bar_width = 1
            ax.bar(normalized_times, body_temperatures, width=bar_width, color='purple', alpha=0.7)
            ax.set_xlabel('Seconds')
            ax.set_ylabel('Body Temperature °C')
            ax.set_title('Body Temperature (Degrees Celsius)')
            ax.grid(axis='y')
            ax.yaxis.set_major_locator(MultipleLocator(1))
            ax.set_ylim(bottom=30)
            canvas = FigureCanvasKivyAgg(fig)
            box2.add_widget(canvas)

        except Exception as e:
            print("Error:", e)

"""
AFNT App class, this function is responsible for rendering the AFNT App and all its contents.
The builder function in AFNTApp renders `screens.kv`, which contains all the screen definations and design (similar to HTML and CSS in websites).
"""
class AFNTApp(MDApp):
    selected_gender = StringProperty("")

    def build(self): # Initializing the LocalDB and ScreenManager
        self.local_db = LocalDB('local_db.db')
        self.water_intake_table = WaterIntake(self.local_db.connection)
        self.weight_table = Weight(self.local_db.connection)
        self.height_table = Height(self.local_db.connection)
        self.bmi_table = BMI(self.local_db.connection)
        self.skeletal_muscle_table = SkeletalMuscle(self.local_db.connection)
        self.body_fat_table = BodyFat(self.local_db.connection)
        self.step_count_table = StepCount(self.local_db.connection)
        self.workout_table = Workout(self.local_db.connection)
        self.workout_log_table = WorkoutLog(self.local_db.connection)
        self.exercise_table = Exercise(self.local_db.connection)
        self.exercise_log_table =ExerciseLog(self.local_db.connection)
        self.User = User()

        return Builder.load_file('screens.kv')

    # Display error popups
    def show_error_popup(self, message):
        popup = PP(message)
        popupwind = Popup(title='Error', content=popup, size_hint=(None, None), size=(250, 150))
        popupwind.open()

    # Display success popups
    def show_success_popup(self, message):
        popup = PP(message)
        popupwind = Popup(title='Success', content=popup, size_hint=(None, None), size=(250, 150))
        popupwind.open()

    # Login screen input handling and validations
    def handle_username_input(self, text):
        screen = self.root.get_screen('login_screen')
        screen.ids.input_username.error = False if text else True

    def handle_password_input(self, text):
        login_screen = self.root.get_screen('login_screen')
        login_screen.ids.input_password.error = False if text else True
    
    def verify_login(self):
        global logged_user
        login_screen = self.root.get_screen('login_screen')
        login_details = [login_screen.ids.input_username.text, login_screen.ids.input_password.text]
        # login_details = ['asuha', '123']
        logged_user = login_details[0]
        print(login_details)

        if login_details[0] == "":
            login_screen.ids.input_username.error = True
            return self.show_error_popup("enter username")
        if login_details[1] == "":
            login_screen.ids.input_password.error = True
            return self.show_error_popup("enter password")
        login_status = self.User.handle_login(login_details)
        if login_status == 0:
            self.root.current = 'dashboard_screen'
        elif login_status == 1:
            return self.show_error_popup("invalid username")
        elif login_status == 2:
            return self.show_error_popup("invalid password")
        
    # Registration screen input handling and validation functions
    def handle_new_username_input(self, text):
        screen = self.root.get_screen('registration_screen')
        screen.ids.input_new_username.error = False if text else True       

    def handle_new_email_input(self, text):
        screen = self.root.get_screen('registration_screen')
        screen.ids.input_new_email.error = False if text else True       

    def handle_new_password_input(self, text):
        screen = self.root.get_screen('registration_screen')
        screen.ids.input_new_password.error = False if text else True

    def handle_new_phone_input(self, text):
        screen = self.root.get_screen('registration_screen')
        screen.ids.input_new_phone.error = False if text else True
    
    def on_save(self, instance, value, date_range):
        screen = self.root.get_screen('registration_screen')
        formatted_date = value.strftime("%Y-%m-%d")
        screen.ids.date_input.text = formatted_date

    def on_cancel(self, instance, value):
        instance.dismiss()

    def handle_new_dob_input(self):
        if not hasattr(self, 'date_dialog'):
            self.date_dialog = MDDatePicker()
            self.date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        self.date_dialog.open()

    def show_gender_menu(self, instance):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Male", "on_release": lambda x="Male": self.select_gender(x, instance)},
            {"viewclass": "OneLineListItem", "text": "Female", "on_release": lambda x="Female": self.select_gender(x, instance)},
        ]
        menu = MDDropdownMenu(items=menu_items, width_mult=4)
        menu.caller = instance
        menu.open()

    def select_gender(self, selected_gender_text, textfield_instance):
        self.selected_gender = selected_gender_text
        textfield_instance.text = self.selected_gender

    def verify_registration(self):
        registration_screen = self.root.get_screen('registration_screen')
        reg_details = [registration_screen.ids.input_new_username.text, registration_screen.ids.input_new_email.text, registration_screen.ids.input_new_password.text,
                         registration_screen.ids.input_new_phone.text, registration_screen.ids.date_input.text, registration_screen.ids.gender_input.text]

        if reg_details[0] == "":
            registration_screen.ids.input_new_username.error = True
            return self.show_error_popup("enter username")
        if reg_details[1] == "":
            registration_screen.ids.input_new_email.error = True
            return self.show_error_popup("enter email")
        if reg_details[2] == "":
            registration_screen.ids.input_new_password.error = True
            return self.show_error_popup("enter password")
        if reg_details[3] == "":
            registration_screen.ids.input_new_phone.error = True
            return self.show_error_popup("enter phone number")
        if reg_details[4] == "":
            registration_screen.ids.date_input.error = True
            return self.show_error_popup("enter date of birth")
        if reg_details[5] == "":
            registration_screen.ids.gender_input.error = True
            return self.show_error_popup("select gender")
        
        reg_status = self.User.handle_registration(reg_details)
        if reg_status == 3:
            return self.show_error_popup("username too long")
        elif reg_status == 4:
            return self.show_error_popup("user already exists")
        elif reg_status == 5:
            return self.show_error_popup("invalid email")
        elif reg_status == 6:
            return self.show_error_popup("email used by another user")
        elif reg_status == 7:
            return self.show_error_popup("password too short")
        elif reg_status == 8:
            return self.show_error_popup("invalid phone number")
        elif reg_status == 9:
            return self.show_error_popup("invalid age")
        elif reg_status == 10:
            return self.show_success_popup("Registration Successfull!")

    # Dashboard screen validations functions
    def handle_dropdown(self, category, instance):
        dashboard_screen = self.root.get_screen('dashboard_screen')
        menu_items = []
        logged_user = 'alisua'

        if category == 'profile':
            menu_items = [
                {"viewclass": "OneLineListItem", "text": "Profile", "on_release": lambda x="Profile": self.selected_navbar_dropdown(x)},
                {"viewclass": "OneLineListItem", "text": "Logout", "on_release": lambda x="Logout": self.logout_and_close_menu(dashboard_screen)},
                {"viewclass": "OneLineListItem", "text": "T&C", "on_release": lambda x="T&C": self.selected_navbar_dropdown(x)},
            ]

        self.menu = MDDropdownMenu(items=menu_items, width_mult=4)
        self.menu.caller = instance
        self.menu.open()

    def selected_navbar_dropdown(self, selected_item_text):
        if hasattr(self, 'menu'):
            self.menu.dismiss()  # Dismiss the menu if it exists

    def logout_and_close_menu(self, dashboard_screen):
        dashboard_screen.logout()
        self.selected_navbar_dropdown("Logout")

    # Water Intake screen input handling and validation functions
    def handle_water_intake_date_input(self):
        if not hasattr(self, 'water_date_dialog'):
            self.water_date_dialog = MDDatePicker()
            self.water_date_dialog.bind(on_save=self.water_on_save, on_cancel=self.on_cancel)
        self.water_date_dialog.open()
    
    def water_on_save(self, instance, value, date_range):
        screen = self.root.get_screen('water_intake_screen')
        formatted_date = value.strftime("%d/%m/%Y")
        screen.ids.water_date_input.text = formatted_date
    
    def handle_water_input(self, text):
        screen = self.root.get_screen('water_intake_screen')
        screen.ids.water_input.error = False if text else True 

    def verify_water_input(self):
        water_intake_screen = self.root.get_screen('water_intake_screen')
        water_details = [water_intake_screen.ids.water_input.text, water_intake_screen.ids.water_date_input.text]

        result_code = self.water_intake_table.verify_water_intake(water_details[0], water_details[1])
        if result_code == 15:
            return self.show_success_popup("water intake recorded\n successfully")
        elif result_code == 14:
            return self.show_error_popup("select date")
        elif result_code == 13:
            return self.show_error_popup("enter valid water intake\n value")
        elif result_code == 12:
            return self.show_error_popup("enter valid water intake\n format")
        elif result_code == 11:
            return self.show_error_popup("water intake length exceeds\n limit")

    def verify_delete_water_intake_data(self):
        self.water_intake_table.remove_all_water_intake()
        self.show_success_popup("all water intake data\n successfully deleted")

    # Body Statistics screen input handling and validation
    def handle_body_stats_date_input(self):
        if not hasattr(self, 'body_stats_date'):
            self.body_stats_date = MDDatePicker()
            self.body_stats_date.bind(on_save=self.body_stats_on_save, on_cancel=self.on_cancel)
        self.body_stats_date.open()
    
    def body_stats_on_save(self, instance, value, date_range):
        screen = self.root.get_screen('body_stats_screen')
        formatted_date = value.strftime("%d/%m/%Y")
        screen.ids.body_stats_date.text = formatted_date

    def handle_weight_input(self, text):
        screen = self.root.get_screen('body_stats_screen')
        screen.ids.weight_input.error = False if text else True

    def verify_date_input(self, date):
        if not date:
            self.show_error_popup("enter date")
            return 21

    def verify_body_stats_input(self):
        body_stats_screen = self.root.get_screen('body_stats_screen')
        body_stats_details = [body_stats_screen.ids.body_stats_date.text, body_stats_screen.ids.weight_input.text, body_stats_screen.ids.height_input.text, 
                              body_stats_screen.ids.body_fat_input.text, body_stats_screen.ids.skeletal_muscle_input.text, body_stats_screen.ids.step_count_input.text]
        
        verify_date = self.verify_date_input(body_stats_details[0])

        weight_code = self.weight_table.verify_weight(body_stats_details[1])
        height_code = self.height_table.verify_height(body_stats_details[2])
        body_fat_code = self.body_fat_table.verify_body_fat(body_stats_details[3])
        skeletal_muscle_code = self.skeletal_muscle_table.verify_skeletal_muscle(body_stats_details[4])
        step_count_code = self.step_count_table.verify_step_count(body_stats_details[5])

        print("weight code:", weight_code)
        print('height code', height_code)
        print("body_fat_code", body_fat_code)
        print("skeletal_muscle_code", skeletal_muscle_code)
        print("step_count_code",step_count_code)

        # Weight validation handling
        if weight_code == 16:
            return self.show_error_popup("invalid weight")
        elif weight_code == 17:
            return self.show_error_popup("weight out of range")
        elif weight_code == 18:
            return self.show_error_popup("weight is a negative number")
        elif weight_code == 19:
            return self.show_error_popup("invalid weight format")
        
        # Height validation handling
        if height_code == 23:
            return self.show_error_popup("invalid height")
        elif height_code == 24:
            self.bmi_table.insert_bmi(float(body_stats_details[1]), float(self.height_table.get_latest_height_value()*100), body_stats_details[0])

        # Skeletal muscle validation handling
        if skeletal_muscle_code == 26:
            return self.show_error_popup("invalid skeletal muscle value")
        elif skeletal_muscle_code == 27:
            print("Err27: no skeletal muscle input")

        # Body fat validation handling
        if body_fat_code == 29:
            return self.show_error_popup("invalid body fat value")
        elif body_fat_code == 30:
            self.body_fat_table.calculate_body_fat(float(body_stats_details[1]), logged_user, body_stats_details[0])
            print("Err27: no body fat input")

        # Step count validation handling
        if step_count_code == 33:
            return self.show_error_popup("invalid step count")
        elif step_count_code == 31:
            print("Err24: no step count input")
        
        # Inserting values in LocalDB
        if weight_code == 20:
            self.weight_table.insert_weight(body_stats_details[1], body_stats_details[0])
        if height_code == 22:
            self.height_table.insert_height(int(body_stats_details[2])/100, body_stats_details[0])
            self.bmi_table.insert_bmi(float(body_stats_details[1]), float(body_stats_details[2]), body_stats_details[0])
        if skeletal_muscle_code == 25:
            self.skeletal_muscle_table.insert_skeletal_muscle(float(body_stats_details[4]), body_stats_details[0])
        if body_fat_code == 28:
            self.body_fat_table.insert_body_fat(float(body_stats_details[1]), float(body_stats_details[3]), body_stats_details[0])
        if step_count_code == 32:
            self.step_count_table.insert_step_count(int(body_stats_details[5]), body_stats_details[0])
        return self.show_success_popup("successfully updated record")

    def on_stop(self):
        self.local_db.close_connection()
