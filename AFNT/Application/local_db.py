import os
import csv
import sqlite3
from csv import DictReader
from io import StringIO
from datetime import date, time, datetime

class LocalDB():
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
            water_tot_g INTEGER,
            energy_tot_kcal INTEGER,
            protein_tot_g REAL,
            lipid_tot_g REAL,
            carbs_tot_g REAL,
            fiber_tot_g REAL,
            sugar_tot_g REAL,
            calcium_tot_mg REAL,
            iron_tot_mg REAL,
            cholestrl_tot_mg REAL,
            serving REAL NOT NULL,
            date_created DATE,
            time_created TIME,
            is_active BOOLEAN NOT NULL
            )"""

        create_meal_logs = """
            CREATE TABLE IF NOT EXISTS meal_logs (
            meal_log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            meal_id TEXT NOT NULL,
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
                    water_tot_g = row['water_tot_g']
                    energy_tot_kcal = row['energy_tot_kcal']
                    protein_tot_g = row['protein_tot_g']
                    lipid_tot_g  = row['lipid_tot_g']
                    carbs_tot_g  = row['carbs_tot_g']
                    fiber_tot_g  = row['fiber_tot_g']
                    sugar_tot_g  = row['sugar_tot_g']
                    calcium_tot_mg  = row['calcium_tot_mg']
                    iron_tot_mg  = row['iron_tot_mg']
                    cholestrl_tot_mg  = row['cholestrl_tot_mg']
                    serving = row['serving']
                    date_created = row['date_created']
                    time_created = row['time_created']
                    is_active = row['is_active']
                
                    sql = """INSERT INTO meals
                             (meal_id, type, description, water_tot_g, energy_tot_kcal, protein_tot_g, lipid_tot_g, carbs_tot_g, fiber_tot_g, sugar_tot_g, calcium_tot_mg, iron_tot_mg, cholestrl_tot_mg, serving, date_created, time_created, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                    values = (meal_id, type, description, water_tot_g, energy_tot_kcal, protein_tot_g, lipid_tot_g, carbs_tot_g, fiber_tot_g, sugar_tot_g, calcium_tot_mg, iron_tot_mg, cholestrl_tot_mg, serving, date_created, time_created, is_active)
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
                    ate = row['ate']
                    date_ate = row['date_ate']
                    time_ate = row['time_ate']
                    is_active = row['is_active']

                    sql = """INSERT INTO meal_logs
                             (meal_log_id, meal_id, ate, date_ate, time_ate, is_active) 
                             VALUES (?, ?, ?, ?, ?, ?)"""
                    values = (meal_log_id, meal_id, ate, date_ate, time_ate, is_active)
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

# class ExerciseTable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_exercise(self, exercise):
#         try:
#             table_name = 'exercises'
#             with self.connection:
#                 self.cursor.execute(f"SELECT MAX(exercise_id) FROM {table_name} WHERE exercise_id LIKE 'C%'")
#                 latest_id = self.cursor.fetchone()[0]

#             new_id_numeric = int(latest_id[1:]) + 1 if latest_id else 1
#             new_id = f'C{new_id_numeric}'

#             exercise['exercise_id'] = new_id

#             columns = ', '.join(key for key in exercise.keys())
#             placeholders = ', '.join(':' + key for key in exercise.keys())
#             sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
#             with self.connection:
#                 self.cursor.execute(sql, exercise)

#         except sqlite3.IntegrityError as e:
#             print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting exercise: {e}")

#     def get_exercise_by_id(self, exercise_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM exercises WHERE exercise_id=?", (exercise_id,))
#             return self.cursor.fetchall()

#     def get_exercise_by_name(self, exercise_name):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM exercises WHERE LOWER(exercise_name) = LOWER(?)", (exercise_name,))
#             return self.cursor.fetchall()

#     def update_exercise(self, exercise_id, updated_values):
#         table_name = 'exercises'

#         # Check if the exercise_id is a custom ID (starts with 'C')
#         if exercise_id.startswith('C'):
#             # If it's a custom ID, update the existing record
#             set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#             sql = f"UPDATE {table_name} SET {set_clause} WHERE exercise_id = :exercise_id"
#             updated_values['exercise_id'] = exercise_id

#             with self.connection:
#                 self.cursor.execute(sql, updated_values)
#         else:
#             # If it's a preset ID, create a copy with a custom ID and update the copy
#             # Assume exercise_id is numeric for preset IDs
#             with self.connection:
#                 self.cursor.execute(f"PRAGMA table_info({table_name})")
#                 columns_info = self.cursor.fetchall()
#                 columns = [column_info[1] for column_info in columns_info]

#                 self.cursor.execute(f"SELECT * FROM {table_name} WHERE exercise_id = ?", (exercise_id,))
#                 existing_record = self.cursor.fetchone()

#                 if existing_record:
#                     # Create a copy with a custom ID (C ID)
#                     new_id_numeric = self._get_next_custom_id_numeric()
#                     new_id = f'C{new_id_numeric}'

#                     # Copy values and update with user-provided values
#                     updated_record = dict(zip(columns, existing_record))
#                     updated_record.update(updated_values)
#                     updated_record['exercise_id'] = new_id

#                     # Insert the updated record with the custom ID
#                     columns = ', '.join(key for key in updated_record.keys())
#                     placeholders = ', '.join(':' + key for key in updated_record.keys())
#                     insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
#                     self.cursor.execute(insert_sql, updated_record)

#     def _get_next_custom_id_numeric(self):
#         # Get the next available numeric part for the custom ID
#         with self.connection:
#             self.cursor.execute("SELECT MAX(CAST(SUBSTR(exercise_id, 2) AS INTEGER)) FROM exercises WHERE exercise_id LIKE 'C%'")
#             latest_id_numeric = self.cursor.fetchone()[0]

#         return latest_id_numeric + 1 if latest_id_numeric else 1

#     def remove_exercise(self, exercise_id):
#         with self.connection:
#             if exercise_id.startswith('C'):
#                 self.cursor.execute("DELETE FROM exercises WHERE exercise_id=?", (exercise_id,))
#             else:
#                 print("Cannot delete preset exercises.")

#     def drop_exercise(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS exercises")

# class ExerciseLogsTable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_exercise_log(self, exercise_log):
#         try:
#             with self.connection:
#                 columns = ', '.join(exercise_log.keys())
#                 values = [exercise_log.get(key, '') for key in exercise_log.keys()]
#                 placeholders = ', '.join('?' for _ in exercise_log.values())

#                 sql = f"""
#                     INSERT INTO exercise_logs 
#                     ({columns}) 
#                     VALUES ({placeholders})
#                 """
#                 self.cursor.execute(sql, values)

#         except sqlite3.IntegrityError as e:
#             if "FOREIGN KEY constraint failed" in str(e):
#                 print("Error: Invalid exercise_id or workout_log_id.")
#             else:
#                 print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting exercise log: {e}")

#     def get_exercise_log_by_id(self, exercise_log_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM exercise_logs WHERE exercise_log_id=?", (exercise_log_id,))
#             return self.cursor.fetchall()

#     def update_exercise_log(self, exercise_log_id, updated_values):
#         table_name = 'exercise_logs'
#         set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#         sql = f"UPDATE {table_name} SET {set_clause} WHERE exercise_log_id = :exercise_log_id"
#         updated_values['exercise_log_id'] = exercise_log_id

#         with self.connection:
#             self.cursor.execute(sql, updated_values)

#     def remove_exercise_log(self, exercise_log_id):
#         with self.connection:
#             self.cursor.execute("DELETE FROM exercise_logs WHERE exercise_log_id=?", (exercise_log_id,))

#     def drop_exercise_log(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS exercise_logs")

# class WorkoutTable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_workout(self, workout):
#         try:
#             table_name = 'workouts'
#             with self.connection:
#                 self.cursor.execute(f"SELECT MAX(workout_id) FROM {table_name} WHERE workout_id LIKE 'C%'")
#                 latest_id = self.cursor.fetchone()[0]

#             new_id_numeric = int(latest_id[1:]) + 1 if latest_id else 1
#             new_id = f'C{new_id_numeric}'

#             workout['workout_id'] = new_id

#             columns = ', '.join(key for key in workout.keys())
#             placeholders = ', '.join(':' + key for key in workout.keys())
#             sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
#             with self.connection:
#                 self.cursor.execute(sql, workout)

#         except sqlite3.IntegrityError as e:
#             print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting workout: {e}")

#     def get_workout_by_id(self, workout_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM workouts WHERE workout_id=?", (workout_id,))
#             return self.cursor.fetchall()

#     def get_workout_by_name(self, workout_name):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM workouts WHERE LOWER(workout_name) = LOWER(?)", (workout_name,))
#             return self.cursor.fetchall()

#     def update_workout(self, workout_id, updated_values):
#         table_name = 'workouts'

#         # Check if the workout_id is a custom ID (starts with 'C')
#         if workout_id.startswith('C'):
#             # If it's a custom ID, update the existing record
#             set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#             sql = f"UPDATE {table_name} SET {set_clause} WHERE workout_id = :workout_id"
#             updated_values['workout_id'] = workout_id

#             with self.connection:
#                 self.cursor.execute(sql, updated_values)
#         else:
#             # If it's a preset ID, create a copy with a custom ID and update the copy
#             # Assume workout_id is numeric for preset IDs
#             with self.connection:
#                 self.cursor.execute(f"PRAGMA table_info({table_name})")
#                 columns_info = self.cursor.fetchall()
#                 columns = [column_info[1] for column_info in columns_info]

#                 self.cursor.execute(f"SELECT * FROM {table_name} WHERE workout_id = ?", (workout_id,))
#                 existing_record = self.cursor.fetchone()

#                 if existing_record:
#                     # Create a copy with a custom ID (C ID)
#                     new_id_numeric = self._get_next_custom_id_numeric()
#                     new_id = f'C{new_id_numeric}'

#                     # Copy values and update with user-provided values
#                     updated_record = dict(zip(columns, existing_record))
#                     updated_record.update(updated_values)
#                     updated_record['workout_id'] = new_id

#                     # Insert the updated record with the custom ID
#                     columns = ', '.join(key for key in updated_record.keys())
#                     placeholders = ', '.join(':' + key for key in updated_record.keys())
#                     insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
#                     self.cursor.execute(insert_sql, updated_record)

#     def _get_next_custom_id_numeric(self):
#         with self.connection:
#             self.cursor.execute("SELECT MAX(CAST(SUBSTR(workout_id, 2) AS INTEGER)) FROM workouts WHERE workout_id LIKE 'C%'")
#             latest_id_numeric = self.cursor.fetchone()[0]

#         return latest_id_numeric + 1 if latest_id_numeric else 1

#     def remove_workout(self, workout_id):
#         with self.connection:
#             if workout_id.startswith('C'):
#                 self.cursor.execute("DELETE FROM workouts WHERE workout_id=?", (workout_id,))
#             else:
#                 print("Cannot delete preset workouts.")

#     def drop_workout(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS workouts")

# class WorkoutLogsTable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_workout_log(self, workout_log):
#         try:
#             with self.connection:
#                 columns = ', '.join(workout_log.keys())
#                 values = [workout_log.get(key, '') for key in workout_log.keys()]
#                 placeholders = ', '.join('?' for _ in workout_log.values())

#                 sql = f"""
#                     INSERT INTO workout_logs 
#                     ({columns}) 
#                     VALUES ({placeholders})
#                 """
#                 self.cursor.execute(sql, values)

#         except sqlite3.IntegrityError as e:
#             if "FOREIGN KEY constraint failed" in str(e):
#                 print("Error: Invalid workout_id or workout_log_id.")
#             else:
#                 print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting workout log: {e}")

#     def get_workout_log_by_id(self, workout_log_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM workout_logs WHERE workout_log_id=?", (workout_log_id,))
#             return self.cursor.fetchall()

#     def update_workout_log(self, workout_log_id, updated_values):
#         table_name = 'workout_logs'
#         set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#         sql = f"UPDATE {table_name} SET {set_clause} WHERE workout_log_id = :workout_log_id"
#         updated_values['workout_log_id'] = workout_log_id

#         with self.connection:
#             self.cursor.execute(sql, updated_values)

#     def remove_workout_log(self, workout_log_id):
#         with self.connection:
#             self.cursor.execute("DELETE FROM workout_logs WHERE workout_log_id=?", (workout_log_id,))

#     def drop_workout_log(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS workout_logs")

class MealTable():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_meal(self, meal):
        try:
            table_name = 'meals'
            with self.connection:
                self.cursor.execute(f"SELECT MAX(meal_id) FROM {table_name} WHERE meal_id LIKE 'C%'")
                latest_id = self.cursor.fetchone()[0]

            new_id_numeric = int(latest_id[1:]) + 1 if latest_id else 1
            new_id = f'C{new_id_numeric}'

            meal['meal_id'] = new_id

            columns = ', '.join(key for key in meal.keys())
            placeholders = ', '.join(':' + key for key in meal.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.connection:
                self.cursor.execute(sql, meal)

        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting meal: {e}")

    def get_meal_by_id(self, meal_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM meals WHERE meal_id=?", (meal_id,))
            return self.cursor.fetchall()

    def get_meal_by_type(self, type):
        with self.connection:
            self.cursor.execute("SELECT * FROM meals WHERE LOWER(type) = LOWER(?)", (type,))
            return self.cursor.fetchall()

    def update_meal(self, meal_id, updated_values):
        table_name = 'meals'

        if meal_id.startswith('C'):
            set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
            sql = f"UPDATE {table_name} SET {set_clause} WHERE meal_id = :meal_id"
            updated_values['meal_id'] = meal_id

            with self.connection:
                self.cursor.execute(sql, updated_values)
        else:
            with self.connection:
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()
                columns = [column_info[1] for column_info in columns_info]

                self.cursor.execute(f"SELECT * FROM {table_name} WHERE meal_id = ?", (meal_id,))
                existing_record = self.cursor.fetchone()

                if existing_record:
                    new_id_numeric = self._get_next_custom_id_numeric()
                    new_id = f'C{new_id_numeric}'

                    updated_record = dict(zip(columns, existing_record))
                    updated_record.update(updated_values)
                    updated_record['meal_id'] = new_id

                    columns = ', '.join(key for key in updated_record.keys())
                    placeholders = ', '.join(':' + key for key in updated_record.keys())
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    self.cursor.execute(insert_sql, updated_record)

    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(meal_id, 2) AS INTEGER)) FROM meals WHERE meal_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    def remove_meal(self, meal_id):
        with self.connection:
            if meal_id.startswith('C'):
                self.cursor.execute("DELETE FROM meals WHERE meal_id=?", (meal_id,))
            else:
                print("Cannot delete preset meals.")

    def drop_meal(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS meals")

class MealLogsTable():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_meal_log(self, meal_log):
        try:
            with self.connection:
                columns = ', '.join(meal_log.keys())
                values = [meal_log.get(key, '') for key in meal_log.keys()]
                placeholders = ', '.join('?' for _ in meal_log.values())

                sql = f"""
                    INSERT INTO meal_logs 
                    ({columns}) 
                    VALUES ({placeholders})
                """
                self.cursor.execute(sql, values)

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid meal_id or workout_log_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting meal log: {e}")

    def get_meal_log_by_id(self, meal_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM meal_logs WHERE meal_log_id=?", (meal_log_id,))
            return self.cursor.fetchall()

    def update_meal_log(self, meal_log_id, updated_values):
        table_name = 'meal_logs'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE meal_log_id = :meal_log_id"
        updated_values['meal_log_id'] = meal_log_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(meal_log_id, 2) AS INTEGER)) FROM meal_logs WHERE meal_log_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    def remove_meal_log(self, meal_log_id):
        with self.connection:
            self.cursor.execute("DELETE FROM meal_logs WHERE meal_log_id=?", (meal_log_id,))

    def drop_meal_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS meal_logs")

class FoodItemsTable():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_food_item(self, food_item):
        try:
            table_name = 'food_items'
            with self.connection:
                self.cursor.execute(f"SELECT MAX(food_item_id) FROM {table_name} WHERE food_item_id LIKE 'C%'")
                latest_id = self.cursor.fetchone()[0]

            new_id_numeric = int(latest_id[1:]) + 1 if latest_id else 1
            new_id = f'C{new_id_numeric}'

            food_item['food_item_id'] = new_id

            columns = ', '.join(key for key in food_item.keys())
            placeholders = ', '.join(':' + key for key in food_item.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.connection:
                self.cursor.execute(sql, food_item)

        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting food_item: {e}")

    def get_food_item_by_id(self, food_item_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM food_items WHERE food_item_id=?", (food_item_id,))
            return self.cursor.fetchall()

    def get_food_item_by_name(self, food_item_name):
        with self.connection:
            self.cursor.execute("SELECT * FROM food_items WHERE LOWER(food_item_name) = LOWER(?)", (food_item_name,))
            return self.cursor.fetchall()

    def update_food_item(self, food_item_id, updated_values):
        table_name = 'food_items'

        if food_item_id.startswith('C'):
            set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
            sql = f"UPDATE {table_name} SET {set_clause} WHERE food_item_id = :food_item_id"
            updated_values['food_item_id'] = food_item_id

            with self.connection:
                self.cursor.execute(sql, updated_values)
        else:
            with self.connection:
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()
                columns = [column_info[1] for column_info in columns_info]

                self.cursor.execute(f"SELECT * FROM {table_name} WHERE food_item_id = ?", (food_item_id,))
                existing_record = self.cursor.fetchone()

                if existing_record:
                    new_id_numeric = self._get_next_custom_id_numeric()
                    new_id = f'C{new_id_numeric}'

                    updated_record = dict(zip(columns, existing_record))
                    updated_record.update(updated_values)
                    updated_record['food_item_id'] = new_id

                    columns = ', '.join(key for key in updated_record.keys())
                    placeholders = ', '.join(':' + key for key in updated_record.keys())
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    self.cursor.execute(insert_sql, updated_record)

    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(food_item_id, 2) AS INTEGER)) FROM food_items WHERE food_item_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    def remove_food_item(self, food_item_id):
        with self.connection:
            if food_item_id.startswith('C'):
                self.cursor.execute("DELETE FROM food_items WHERE food_item_id=?", (food_item_id,))
            else:
                print("Cannot delete preset food_items.")

    def drop_food_item(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS food_items")

class FoodItemLogsTable():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_food_item_log(self, food_item_log):
        try:
            with self.connection:
                columns = ', '.join(food_item_log.keys())
                values = [food_item_log.get(key, '') for key in food_item_log.keys()]
                placeholders = ', '.join('?' for _ in food_item_log.values())

                sql = f"""
                    INSERT INTO food_item_logs 
                    ({columns}) 
                    VALUES ({placeholders})
                """
                self.cursor.execute(sql, values)

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid food_item_id or workout_log_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting food_item log: {e}")

    def get_food_item_log_by_id(self, food_item_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM food_item_logs WHERE food_item_log_id=?", (food_item_log_id,))
            return self.cursor.fetchall()

    def update_food_item_log(self, food_item_log_id, updated_values):
        table_name = 'food_item_logs'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE food_item_log_id = :food_item_log_id"
        updated_values['food_item_log_id'] = food_item_log_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(food_item_log_id, 2) AS INTEGER)) FROM food_item_logs WHERE food_item_log_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    def remove_food_item_log(self, food_item_log_id):
        with self.connection:
            self.cursor.execute("DELETE FROM food_item_logs WHERE food_item_log_id=?", (food_item_log_id,))

    def drop_food_item_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS food_item_logs")

# class BMITable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_bmi(self, bmi):
#         try:
#             with self.connection:
#                 columns = ', '.join(bmi.keys())
#                 values = [bmi.get(key, '') for key in bmi.keys()]
#                 placeholders = ', '.join('?' for _ in bmi.values())

#                 sql = f"""
#                     INSERT INTO bmi 
#                     ({columns}) 
#                     VALUES ({placeholders})
#                 """
#                 self.cursor.execute(sql, values)

#         except sqlite3.IntegrityError as e:
#             if "FOREIGN KEY constraint failed" in str(e):
#                 print("Error: Invalid workout_id or bmi_id.")
#             else:
#                 print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting workout log: {e}")

#     def get_bmi_by_id(self, bmi_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM bmi WHERE bmi_id=?", (bmi_id,))
#             return self.cursor.fetchall()

#     def update_bmi(self, bmi_id, updated_values):
#         table_name = 'bmi'
#         set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#         sql = f"UPDATE {table_name} SET {set_clause} WHERE bmi_id = :bmi_id"
#         updated_values['bmi_id'] = bmi_id

#         with self.connection:
#             self.cursor.execute(sql, updated_values)

#     def remove_bmi(self, bmi_id):
#         with self.connection:
#             self.cursor.execute("DELETE FROM bmi WHERE bmi_id=?", (bmi_id,))

#     def drop_bmi(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS bmi")

# class BodyFatTable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_body_fat(self, body_fat):
#         try:
#             with self.connection:
#                 columns = ', '.join(body_fat.keys())
#                 values = [body_fat.get(key, '') for key in body_fat.keys()]
#                 placeholders = ', '.join('?' for _ in body_fat.values())

#                 sql = f"""
#                     INSERT INTO body_fat 
#                     ({columns}) 
#                     VALUES ({placeholders})
#                 """
#                 self.cursor.execute(sql, values)

#         except sqlite3.IntegrityError as e:
#             if "FOREIGN KEY constraint failed" in str(e):
#                 print("Error: Invalid workout_id or body_fat_id.")
#             else:
#                 print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting workout log: {e}")

#     def get_body_fat_by_id(self, body_fat_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM body_fat WHERE body_fat_id=?", (body_fat_id,))
#             return self.cursor.fetchall()

#     def update_body_fat(self, body_fat_id, updated_values):
#         table_name = 'body_fat'
#         set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#         sql = f"UPDATE {table_name} SET {set_clause} WHERE body_fat_id = :body_fat_id"
#         updated_values['body_fat_id'] = body_fat_id

#         with self.connection:
#             self.cursor.execute(sql, updated_values)

#     def remove_body_fat(self, body_fat_id):
#         with self.connection:
#             self.cursor.execute("DELETE FROM body_fat WHERE body_fat_id=?", (body_fat_id,))

#     def drop_body_fat(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS body_fat")

# class SkeletalMuscleTable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_skeletal_muscle(self, skeletal_muscle):
#         try:
#             with self.connection:
#                 columns = ', '.join(skeletal_muscle.keys())
#                 values = [skeletal_muscle.get(key, '') for key in skeletal_muscle.keys()]
#                 placeholders = ', '.join('?' for _ in skeletal_muscle.values())

#                 sql = f"""
#                     INSERT INTO skeletal_muscle 
#                     ({columns}) 
#                     VALUES ({placeholders})
#                 """
#                 self.cursor.execute(sql, values)

#         except sqlite3.IntegrityError as e:
#             if "FOREIGN KEY constraint failed" in str(e):
#                 print("Error: Invalid workout_id or skeletal_muscle_id.")
#             else:
#                 print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting workout log: {e}")

#     def get_skeletal_muscle_by_id(self, skeletal_muscle_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM skeletal_muscle WHERE skeletal_muscle_id=?", (skeletal_muscle_id,))
#             return self.cursor.fetchall()

#     def update_skeletal_muscle(self, skeletal_muscle_id, updated_values):
#         table_name = 'skeletal_muscle'
#         set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#         sql = f"UPDATE {table_name} SET {set_clause} WHERE skeletal_muscle_id = :skeletal_muscle_id"
#         updated_values['skeletal_muscle_id'] = skeletal_muscle_id

#         with self.connection:
#             self.cursor.execute(sql, updated_values)

#     def remove_skeletal_muscle(self, skeletal_muscle_id):
#         with self.connection:
#             self.cursor.execute("DELETE FROM skeletal_muscle WHERE skeletal_muscle_id=?", (skeletal_muscle_id,))

#     def drop_skeletal_muscle(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS skeletal_muscle")

# class HeightTable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_height(self, height):
#         try:
#             with self.connection:
#                 columns = ', '.join(height.keys())
#                 values = [height.get(key, '') for key in height.keys()]
#                 placeholders = ', '.join('?' for _ in height.values())

#                 sql = f"""
#                     INSERT INTO height 
#                     ({columns}) 
#                     VALUES ({placeholders})
#                 """
#                 self.cursor.execute(sql, values)

#         except sqlite3.IntegrityError as e:
#             if "FOREIGN KEY constraint failed" in str(e):
#                 print("Error: Invalid workout_id or height_id.")
#             else:
#                 print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting workout log: {e}")

#     def get_height_by_id(self, height_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM height WHERE height_id=?", (height_id,))
#             return self.cursor.fetchall()

#     def update_height(self, height_id, updated_values):
#         table_name = 'height'
#         set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#         sql = f"UPDATE {table_name} SET {set_clause} WHERE height_id = :height_id"
#         updated_values['height_id'] = height_id

#         with self.connection:
#             self.cursor.execute(sql, updated_values)

#     def remove_height(self, height_id):
#         with self.connection:
#             self.cursor.execute("DELETE FROM height WHERE height_id=?", (height_id,))

#     def drop_height(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS height")

# class WeightTable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_weight(self, weight):
#         try:
#             with self.connection:
#                 columns = ', '.join(weight.keys())
#                 values = [weight.get(key, '') for key in weight.keys()]
#                 placeholders = ', '.join('?' for _ in weight.values())

#                 sql = f"""
#                     INSERT INTO weight 
#                     ({columns}) 
#                     VALUES ({placeholders})
#                 """
#                 self.cursor.execute(sql, values)

#         except sqlite3.IntegrityError as e:
#             if "FOREIGN KEY constraint failed" in str(e):
#                 print("Error: Invalid workout_id or weight_id.")
#             else:
#                 print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting workout log: {e}")

#     def get_weight_by_id(self, weight_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM weight WHERE weight_id=?", (weight_id,))
#             return self.cursor.fetchall()

#     def update_weight(self, weight_id, updated_values):
#         table_name = 'weight'
#         set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#         sql = f"UPDATE {table_name} SET {set_clause} WHERE weight_id = :weight_id"
#         updated_values['weight_id'] = weight_id

#         with self.connection:
#             self.cursor.execute(sql, updated_values)

#     def remove_weight(self, weight_id):
#         with self.connection:
#             self.cursor.execute("DELETE FROM weight WHERE weight_id=?", (weight_id,))

#     def drop_weight(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS weight")

# class WaterIntakeTable():
#     def __init__(self, connection):
#         self.connection = connection
#         self.cursor = connection.cursor()

#     def insert_water_intake(self, water_intake):
#         try:
#             with self.connection:
#                 columns = ', '.join(water_intake.keys())
#                 values = [water_intake.get(key, '') for key in water_intake.keys()]
#                 placeholders = ', '.join('?' for _ in water_intake.values())

#                 sql = f"""
#                     INSERT INTO water_intake 
#                     ({columns}) 
#                     VALUES ({placeholders})
#                 """
#                 self.cursor.execute(sql, values)

#         except sqlite3.IntegrityError as e:
#             if "FOREIGN KEY constraint failed" in str(e):
#                 print("Error: Invalid workout_id or water_intake_id.")
#             else:
#                 print(f"IntegrityError: {e}")

#         except Exception as e:
#             print(f"Error inserting workout log: {e}")

#     def get_water_intake_by_id(self, water_intake_id):
#         with self.connection:
#             self.cursor.execute("SELECT * FROM water_intake WHERE water_intake_id=?", (water_intake_id,))
#             return self.cursor.fetchall()

#     def update_water_intake(self, water_intake_id, updated_values):
#         table_name = 'water_intake'
#         set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
#         sql = f"UPDATE {table_name} SET {set_clause} WHERE water_intake_id = :water_intake_id"
#         updated_values['water_intake_id'] = water_intake_id

#         with self.connection:
#             self.cursor.execute(sql, updated_values)

#     def remove_water_intake(self, water_intake_id):
#         with self.connection:
#             self.cursor.execute("DELETE FROM water_intake WHERE water_intake_id=?", (water_intake_id,))

#     def drop_water_intake(self):
#         with self.connection:
#             self.cursor.execute("DROP TABLE IF EXISTS water_intake")

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