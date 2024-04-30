import os
import csv
import sqlite3
from csv import DictReader
from io import StringIO
from datetime import date, time, datetime

"""
LocalDB Class that stores all User Workout, Meal and Body Data in a SQLite Database.
This class is responsible for creating localDB tables and intialising it and import data from the CSV file.
"""
class LocalDB():

    # Initializing LocalDB connection
    def __init__(self, local_db):
        self.local_db = local_db
        self.connection = sqlite3.connect(self.local_db)
        self.cursor = self.connection.cursor()
        print("\nLocalDB Connection Established!\n")

    def create_local_db_tables(self):
        create_exercises = """
            CREATE TABLE IF NOT EXISTS exercises (
            exercise_id TEXT PRIMARY KEY NOT NULL,
            exercise_name TEXT NOT NULL,
            description TEXT,
            type TEXT,
            body_part TEXT NOT NULL,
            equipment TEXT,
            level TEXT,
            rating REAL,
            rating_description TEXT,
            is_active BOOLEAN NOT NULL
            )"""

        create_exercise_logs = """
            CREATE TABLE IF NOT EXISTS exercise_logs (
            exercise_log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            exercise_id TEXT NOT NULL,
            workout_log_id INTEGER NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight_kg REAL,
            rest_per_set_s INTEGER,
            duration TEXT,
            distance_m INTEGER,
            rpe REAL,
            is_complete BOOLEAN NOT NULL,
            date_complete DATE,
            time_complete TIME,
            details TEXT,
            is_active BOOLEAN NOT NULL,
            FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id),
            FOREIGN KEY (workout_log_id) REFERENCES workout_logs(workout_log_id)
            )"""
        
        create_workouts = """
            CREATE TABLE IF NOT EXISTS workouts (
            workout_id TEXT PRIMARY KEY NOT NULL,
            workout_name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            date_created DATE,
            level TEXT,
            rating REAL,
            rating_description TEXT,
            time_created TIME,
            is_active BOOLEAN NOT NULL
            )"""

        create_workout_logs = """
            CREATE TABLE IF NOT EXISTS workout_logs (
            workout_log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            workout_id TEXT NOT NULL,
            date_assigned DATE NOT NULL,
            time_assigned TIME NOT NULL,
            is_complete BOOLEAN NOT NULL,
            date_completed DATE,
            time_completed TIME,
            is_active BOOLEAN NOT NULL,
            FOREIGN KEY (workout_id) REFERENCES workouts(id)
            )"""

        create_food_items = """
            CREATE TABLE IF NOT EXISTS food_items (
            food_item_id TEXT PRIMARY KEY NOT NULL,
            food_item_name TEXT NOT NULL,
            water_g INTEGER,
            energy_kcal INTEGER,
            protein_g REAL,
            lipid_g REAL,
            carbs_g REAL,
            fiber_td_g REAL,
            sugar_g REAL,
            calcium_mg REAL,
            iron_mg REAL,
            cholestrl_mg REAL,
            gmwt_1 TEXT,
            gmwt_desc1 TEXT,
            gmwt_2 TEXT,
            gmwt_desc2 TEXT,
            is_active BOOLEAN NOT NULL
            )"""
        
        create_food_item_logs = """
            CREATE TABLE IF NOT EXISTS food_item_logs (
            food_item_log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            meal_log_id INTEGER NOT NULL,
            food_item_id TEXT NOT NULL,
            serving REAL,
            weight_g REAL,
            ate BOOLEAN NOT NULL,
            date_ate DATE,
            time_ate TIME,
            description TEXT,
            is_active BOOLEAN NOT NULL,
            FOREIGN KEY (food_item_id) REFERENCES food_items(food_item_id),
            FOREIGN KEY (meal_log_id) REFERENCES meal_logs(meal_log_id)
            )"""

        create_meals = """
            CREATE TABLE IF NOT EXISTS meals (
            meal_id TEXT PRIMARY KEY NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            date_created DATE,
            time_created TIME,
            is_active BOOLEAN NOT NULL
            )"""

        create_meal_logs = """
            CREATE TABLE IF NOT EXISTS meal_logs (
            meal_log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            meal_id TEXT NOT NULL,
            energy_tot_kcal INTEGER,
            protein_tot_g REAL,
            lipid_tot_g REAL,
            carbs_tot_g REAL,
            fiber_tot_g REAL,
            sugar_tot_g REAL,
            calcium_tot_mg REAL,
            iron_tot_mg REAL,
            ate BOOLEAN NOT NULL,
            date_ate DATE,
            time_ate TIME,
            is_active BOOLEAN NOT NULL,
            FOREIGN KEY (meal_id) REFERENCES meals(meal_id)
            )"""

        create_bmi = """
            CREATE TABLE IF NOT EXISTS bmi (
            bmi_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            bmi REAL NOT NULL,
            date_recorded DATE NOT NULL,
            time_recorded TIME NOT NULL
            )"""

        create_body_fat = """
            CREATE TABLE IF NOT EXISTS body_fat (
            body_fat_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            body_fat_kg REAL NOT NULL,
            date_recorded DATE NOT NULL,
            time_recorded TIME NOT NULL,
            body_fat_percent REAL NOT NULL
            )"""

        create_skeletal_muscle = """
            CREATE TABLE IF NOT EXISTS skeletal_muscle (
            skeletal_muscle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            skeletal_muscle_kg REAL NOT NULL,
            date_recorded DATE NOT NULL,
            time_recorded TIME NOT NULL
            )"""

        create_height = """
            CREATE TABLE IF NOT EXISTS height (
            height_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            height_m REAL NOT NULL,
            date_recorded DATE NOT NULL,
            time_recorded TIME NOT NULL
            )"""

        create_weight = """
            CREATE TABLE IF NOT EXISTS weight (
            weight_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            weight_kg REAL NOT NULL,
            date_recorded DATE NOT NULL,
            time_recorded TIME NOT NULL
            )"""

        create_water_intake = """
            CREATE TABLE IF NOT EXISTS water_intake (
            water_intake_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            water_intake_ml REAL NOT NULL,
            date_recorded DATE NOT NULL,
            time_recorded TIME NOT NULL
            )"""

        create_step_count = """
            CREATE TABLE IF NOT EXISTS step_count (
            step_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            step INTEGER NOT NULL,
            date_recorded DATE NOT NULL,
            time_recorded TIME NOT NULL
            )"""

        # create_blood_oxygen = """"""
        # create_advises = """"""

        tables = [create_exercises, create_exercise_logs, create_workouts, create_workout_logs, create_food_items, create_food_item_logs, 
                  create_meals, create_meal_logs, create_bmi, create_body_fat, create_skeletal_muscle, create_height, create_weight, create_water_intake, create_step_count]

        for table in tables:
            self.cursor.execute(table)
        self.connection.commit()

    def import_exercises_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    exercise_id = row['exercise_id']
                    exercise_name = row['exercise_name']
                    description = row['description']
                    type = row['type']
                    body_part = row['body_part']
                    equipment = row['equipment']
                    level = row['level']
                    rating = row['rating']
                    rating_description = row['rating_description']
                    is_active = row['is_active']

                    # Construct and execute the SQL INSERT statement
                    sql = """INSERT INTO exercises 
                             (exercise_id, exercise_name, description, type, body_part, equipment, level, rating, rating_description, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                    values = (exercise_id, exercise_name, description, type, body_part, equipment, level, rating, rating_description, is_active)
                    self.cursor.execute(sql, values)

            # Commit the changes
            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")

    def import_exercise_logs_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = DictReader(file)
                for row in reader:
                    exercise_log_id = row['exercise_log_id']
                    exercise_id = row['exercise_id']
                    workout_log_id = row['workout_log_id']
                    sets = (row['sets'])
                    reps = (row['reps'])
                    weight_kg = (row['weight_kg'])
                    rest_per_set_s = row['rest_per_set_s']
                    duration = row['duration']
                    distance_m = row['distance_m']
                    rpe = (row['rpe'])
                    is_complete = row['is_complete']
                    date_complete = row['date_complete']
                    time_complete =  row['time_complete']
                    details = row['details']
                    is_active = row['is_active']

                    sql = """INSERT INTO exercise_logs 
                             (exercise_log_id, exercise_id, workout_log_id, sets, reps, weight_kg, rest_per_set_s,
                              duration, distance_m, rpe, is_complete, date_complete, time_complete,
                              details, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                    values = (exercise_log_id, exercise_id, workout_log_id, sets, reps, weight_kg, rest_per_set_s,
                              duration, distance_m, rpe, is_complete, date_complete, time_complete,
                              details, is_active)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")

    def import_workouts_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    workout_id = row['workout_id']
                    workout_name = row['workout_name']
                    description = row['description']
                    type = row['type']
                    date_created = row['date_created']
                    level = row['level']
                    rating = row['rating']
                    rating_description = row['rating_description']
                    time_created = row['time_created']
                    is_active = row['is_active']

                    sql = """INSERT INTO workouts 
                             (workout_id, workout_name, description, type, date_created, level, rating, rating_description, time_created, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                    values = (workout_id, workout_name, description, type, date_created, level, rating, rating_description, time_created, is_active)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")   

    def import_workout_logs_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    workout_log_id = row['workout_log_id']
                    workout_id = row['workout_id']
                    date_assigned = row['date_assigned']
                    time_assigned = row['time_assigned']
                    is_complete = row['is_complete']
                    date_completed = row['date_completed']
                    time_completed = row['time_completed']
                    is_active = row['is_active']

                    sql = """INSERT INTO workout_logs
                             (workout_log_id, workout_id, date_assigned, time_assigned, is_complete, date_completed, time_completed, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
                    values = (workout_log_id, workout_id, date_assigned, time_assigned, is_complete, date_completed, time_completed, is_active)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")   

    def import_food_items_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    food_item_id = row['food_item_id']
                    food_item_name = row['food_item_name']
                    water_g = row['water_g']
                    energy_kcal = row['energy_kcal']
                    protein_g = row['protein_g']
                    lipid_g  = row['lipid_g']
                    carbs_g  = row['carbs_g']
                    fiber_td_g  = row['fiber_td_g']
                    sugar_g  = row['sugar_g']
                    calcium_mg  = row['calcium_mg']
                    iron_mg  = row['iron_mg']
                    cholestrl_mg  = row['cholestrl_mg']
                    gmwt_1 = row['gmwt_1']
                    gmwt_desc1 = row['gmwt_desc1']
                    gmwt_2 = row['gmwt_2']
                    gmwt_desc2 = row['gmwt_desc2']
                    is_active = row['is_active']

                    sql = """INSERT INTO food_items
                             (food_item_id, food_item_name, water_g, energy_kcal, protein_g, lipid_g, carbs_g, fiber_td_g, sugar_g, calcium_mg, iron_mg, cholestrl_mg, gmwt_1, gmwt_desc1, gmwt_2, gmwt_desc2, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                    values = (food_item_id, food_item_name, water_g, energy_kcal, protein_g, lipid_g, carbs_g, fiber_td_g, sugar_g, calcium_mg, iron_mg, cholestrl_mg, gmwt_1, gmwt_desc1, gmwt_2, gmwt_desc2, is_active)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")

    def import_food_item_logs_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    food_item_log_id = row['food_item_log_id']
                    meal_log_id = row['meal_log_id']
                    food_item_id = row['food_item_id']
                    serving = row['serving']
                    weight_g = row['weight_g']
                    ate = row['ate']
                    date_ate = row['date_ate']
                    time_ate = row['time_ate']
                    description = row['description']
                    is_active = row['is_active']

                    sql = """INSERT INTO food_item_logs
                             (food_item_log_id, meal_log_id, food_item_id, serving, weight_g, ate, date_ate, time_ate, description, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                    values = (food_item_log_id, meal_log_id, food_item_id, serving, weight_g, ate, date_ate, time_ate, description, is_active)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")   

    def import_meals_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    meal_id = row['meal_id']
                    type = row['type']
                    description = row['description']
                    date_created = row['date_created']
                    time_created = row['time_created']
                    is_active = row['is_active']
                
                    sql = """INSERT INTO meals
                             (meal_id, type, description, date_created, time_created, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?)"""
                    values = (meal_id, type, description, date_created, time_created, is_active)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")

    def import_meal_logs_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    meal_log_id = row['meal_log_id']
                    meal_id = row['meal_id']
                    energy_tot_kcal = row['energy_tot_kcal']
                    protein_tot_g = row['protein_tot_g']
                    lipid_tot_g  = row['lipid_tot_g']
                    carbs_tot_g  = row['carbs_tot_g']
                    fiber_tot_g  = row['fiber_tot_g']
                    sugar_tot_g  = row['sugar_tot_g']
                    calcium_tot_mg  = row['calcium_tot_mg']
                    iron_tot_mg  = row['iron_tot_mg']
                    ate = row['ate']
                    date_ate = row['date_ate']
                    time_ate = row['time_ate']
                    is_active = row['is_active']

                    sql = """INSERT INTO meal_logs
                             (meal_log_id, meal_id, energy_tot_kcal, protein_tot_g, lipid_tot_g, carbs_tot_g, fiber_tot_g, sugar_tot_g, calcium_tot_mg, iron_tot_mg, ate, date_ate, time_ate, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                    values = (meal_log_id, meal_id, energy_tot_kcal, protein_tot_g, lipid_tot_g, carbs_tot_g, fiber_tot_g, sugar_tot_g, calcium_tot_mg, iron_tot_mg, ate, date_ate, time_ate, is_active)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")   

    def import_bmi_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    bmi_id = row['bmi_id']
                    bmi = row['bmi']
                    date_recorded = row['date_recorded']
                    time_recorded = row['time_recorded']

                    sql = """INSERT INTO bmi
                             (bmi_id, bmi, date_recorded, time_recorded) 
                             VALUES (?, ?, ?, ?)"""
                    values = (bmi_id, bmi, date_recorded, time_recorded)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")   

    def import_body_fat_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    body_fat_id = row['body_fat_id']
                    body_fat_kg = row['body_fat_kg']
                    date_recorded = row['date_recorded']
                    time_recorded = row['time_recorded']
                    body_fat_percent = row['body_fat_percent']

                    sql = """INSERT INTO body_fat
                             (body_fat_id, body_fat_kg, date_recorded, time_recorded, body_fat_percent) 
                             VALUES (?, ?, ?, ?, ?)"""
                    values = (body_fat_id, body_fat_kg, date_recorded, time_recorded, body_fat_percent)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")   

    def import_skeletal_muscle_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    skeletal_muscle_id = row['skeletal_muscle_id']
                    skeletal_muscle_kg = row['skeletal_muscle_kg']
                    date_recorded = row['date_recorded']
                    time_recorded = row['time_recorded']

                    sql = """INSERT INTO skeletal_muscle
                             (skeletal_muscle_id, skeletal_muscle_kg, date_recorded, time_recorded) 
                             VALUES (?, ?, ?, ?)"""
                    values = (skeletal_muscle_id, skeletal_muscle_kg, date_recorded, time_recorded)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")   

    def import_height_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    height_id = row['height_id']
                    height_m = row['height_m']
                    date_recorded = row['date_recorded']
                    time_recorded = row['time_recorded']

                    sql = """INSERT INTO height
                             (height_id, height_m, date_recorded, time_recorded) 
                             VALUES (?, ?, ?, ?)"""
                    values = (height_id, height_m, date_recorded, time_recorded)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")

    def import_weight_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    weight_id = row['weight_id']
                    weight_kg = row['weight_kg']
                    date_recorded = row['date_recorded']
                    time_recorded = row['time_recorded']

                    sql = """INSERT INTO weight
                             (weight_id, weight_kg, date_recorded, time_recorded) 
                             VALUES (?, ?, ?, ?)"""
                    values = (weight_id, weight_kg, date_recorded, time_recorded)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")

    def import_water_intake_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    water_intake_id = row['water_intake_id']
                    water_intake_ml = row['water_intake_ml']
                    date_recorded = row['date_recorded']
                    time_recorded = row['time_recorded']

                    sql = """INSERT INTO water_intake
                             (water_intake_id, water_intake_ml, date_recorded, time_recorded) 
                             VALUES (?, ?, ?, ?)"""
                    values = (water_intake_id, water_intake_ml, date_recorded, time_recorded)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")   

    def import_step_count_from_csv(self, csv_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, csv_file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:

                    step_id = row['step_id']
                    step = row['step']
                    date_recorded = row['date_recorded']
                    time_recorded = row['time_recorded']

                    sql = """INSERT INTO step_count
                             (step_id, step, date_recorded, time_recorded) 
                             VALUES (?, ?, ?, ?)"""
                    values = (step_id, step, date_recorded, time_recorded)
                    self.cursor.execute(sql, values)

            self.connection.commit()
        else:
            print(f"File not found: {csv_file_path}")

    def print_exercises(self):
        sql = "SELECT * FROM exercises"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_exercise_logs(self):
        sql = "SELECT * FROM exercise_logs"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)  

    def print_workouts(self):
        sql = "SELECT * FROM workouts"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)    

    def print_workout_logs(self):
        sql = "SELECT * FROM workout_logs"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_food_items(self):
        sql = "SELECT * FROM food_items"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_food_item_logs(self):
        sql = "SELECT * FROM food_item_logs"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_meals(self):
        sql = "SELECT * FROM meals"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_meal_logs(self):
        sql = "SELECT * FROM meal_logs"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_bmi(self):
        sql = "SELECT * FROM bmi"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_body_fat(self):
        sql = "SELECT * FROM body_fat"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_skeletal_muscle(self):
        sql = "SELECT * FROM skeletal_muscle"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_height(self):
        sql = "SELECT * FROM height"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_weight(self):
        sql = "SELECT * FROM weight"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_water_intake(self):
        sql = "SELECT * FROM water_intake"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def print_step_count(self):
        sql = "SELECT * FROM step_count"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def close_connection(self):
        self.connection.close()
        print("\nLocalDB Connection Closed")

"""
create localDB and import data from CSV files
"""
# db = LocalDB('local_db.db')
# db.create_local_db_tables()
# db.import_exercise_logs_from_csv(r'..\Database\DatabaseCSV\Local\exercise_logs.csv')
# db.import_exercises_from_csv(r'..\Database\DatabaseCSV\Local\exercises.csv')
# db.import_workouts_from_csv(r'..\Database\DatabaseCSV\Local\workouts.csv')
# db.import_workout_logs_from_csv(r'..\Database\DatabaseCSV\Local\workout_logs.csv')
# db.import_food_items_from_csv(r'..\Database\DatabaseCSV\Local\food_items.csv')
# db.import_food_item_logs_from_csv(r'..\Database\DatabaseCSV\Local\food_item_logs.csv')
# db.import_meals_from_csv(r'..\Database\DatabaseCSV\Local\meals.csv')
# db.import_meal_logs_from_csv(r'..\Database\DatabaseCSV\Local\meal_logs.csv')
# db.import_bmi_from_csv(r'..\Database\DatabaseCSV\Local\bmi.csv')
# db.import_body_fat_from_csv(r'..\Database\DatabaseCSV\Local\body_fat.csv')
# db.import_skeletal_muscle_from_csv(r'..\Database\DatabaseCSV\Local\skeletal_muscle.csv')
# db.import_height_from_csv(r'..\Database\DatabaseCSV\Local\height.csv')
# db.import_weight_from_csv(r'..\Database\DatabaseCSV\Local\weight.csv')
# db.import_water_intake_from_csv(r'..\Database\DatabaseCSV\Local\water_intake.csv')
# db.import_step_count_from_csv(r'..\Database\DatabaseCSV\Local\step_count.csv')

# db.print_step_count()
# db.close_connection()