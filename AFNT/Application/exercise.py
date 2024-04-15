from datetime import datetime
import sqlite3
from local_db import LocalDB

"""
This class handles all database and other operations related to the `body_fat` table from LocalDB.
"""
class Exercise():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    # Function for adding new exercise record into the database
    def insert_exercise(self, exercise):
        try:
            table_name = 'exercises'

            with self.connection:
                self.cursor.execute(f"SELECT MAX(CAST(SUBSTR(exercise_id, 2) AS INTEGER)) FROM {table_name} WHERE exercise_id LIKE 'C%'")
                latest_id = self.cursor.fetchone()[0]

            latest_numeric_part = int(latest_id)
            new_id_numeric = latest_numeric_part + 1
            new_id = f'C{new_id_numeric}'

            exercise['exercise_id'] = new_id

            columns = ', '.join(exercise.keys())
            placeholders = ', '.join(':' + key for key in exercise.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            with self.connection:
                self.cursor.execute(sql, exercise)

        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting exercise: {e}")

    # Get exercise record by exercise_id
    def get_exercise_by_id(self, exercise_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM exercises WHERE exercise_id=?", (exercise_id,))
            return self.cursor.fetchall()

    # Get exercise by exercise_name
    def get_exercise_by_name(self, exercise_name):
        with self.connection:
            self.cursor.execute("SELECT * FROM exercises WHERE LOWER(exercise_name) = LOWER(?)", (exercise_name,))
            return self.cursor.fetchall()

    # Get all exercise records (selected columns)
    def get_all_exercises(self):
        with self.connection:
            self.cursor.execute("SELECT exercise_id, exercise_name, type, body_part, equipment, level, rating FROM exercises")
            return self.cursor.fetchall()

    # Update exercise record using exercise_id and updating the values using `updated_values` dictionary
    def update_exercise(self, exercise_id, updated_values):
        table_name = 'exercises'

        # For updating custom exercises (exercise_id starts with 'C')
        if exercise_id.startswith('C'):
            set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
            sql = f"UPDATE {table_name} SET {set_clause} WHERE exercise_id = :exercise_id"
            updated_values['exercise_id'] = exercise_id

            with self.connection:
                self.cursor.execute(sql, updated_values)
        
        # For updating preset exercises (Creates a new exercise, with the same definations as the preset exercise)
        else:
            with self.connection:
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()
                columns = [column_info[1] for column_info in columns_info]

                self.cursor.execute(f"SELECT * FROM {table_name} WHERE exercise_id = ?", (exercise_id,))
                existing_record = self.cursor.fetchone()

                if existing_record:
                    new_id_numeric = self._get_next_custom_id_numeric()
                    new_id = f'C{new_id_numeric}'

                    updated_record = dict(zip(columns, existing_record))
                    updated_record.update(updated_values)
                    updated_record['exercise_id'] = new_id

                    columns = ', '.join(key for key in updated_record.keys())
                    placeholders = ', '.join(':' + key for key in updated_record.keys())
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    self.cursor.execute(insert_sql, updated_record)

    # For handling custom exercises, where exercise_id starts with 'C' as compared with preset exercises whose exercise_ids are integers
    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(exercise_id, 2) AS INTEGER)) FROM exercises WHERE exercise_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    # Function for removing the exercise by setting `is_active` field to `0`. The database will only display those records with is_active = 1
    def remove_exercise(self, exercise_id):
        with self.connection:
            if exercise_id.startswith('C'):
                self.cursor.execute("UPDATE exercises SET is_active = 0 WHERE exercise_id=?", (exercise_id,))
            else:
                print("Cannot delete preset exercises.")
                return 0

    # Function to readd the removed exercises by setting its is_active to 1.
    def re_add_workout(self, workout_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE exercises SET is_active = 1 WHERE exercise_id=?", (workout_id,))
        except Exception as e:
            print(f"Error removing workout log: {e}")

    # Drops the exercises table from LocalDB
    def drop_exercise(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS exercises")
