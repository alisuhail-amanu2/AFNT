from datetime import datetime
import sqlite3
from local_db import LocalDB
import re

class Exercise():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_exercise(self, exercise):
        try:
            table_name = 'exercises'

            # Fetch the latest exercise_id
            with self.connection:
                self.cursor.execute(f"SELECT MAX(CAST(SUBSTR(exercise_id, 2) AS INTEGER)) FROM {table_name} WHERE exercise_id LIKE 'C%'")
                latest_id = self.cursor.fetchone()[0]

            latest_numeric_part = int(latest_id)

            # Generate the new exercise_id
            new_id_numeric = latest_numeric_part + 1
            new_id = f'C{new_id_numeric}'

            exercise['exercise_id'] = new_id

            # Prepare the SQL query
            columns = ', '.join(exercise.keys())
            placeholders = ', '.join(':' + key for key in exercise.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # Execute the SQL query with the new exercise data
            with self.connection:
                self.cursor.execute(sql, exercise)

        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")
            # Handle integrity constraint violation appropriately
            # For example, log the error or raise an exception

        except Exception as e:
            print(f"Error inserting exercise: {e}")




    def get_exercise_by_id(self, exercise_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM exercises WHERE exercise_id=?", (exercise_id,))
            return self.cursor.fetchall()

    def get_exercise_by_name(self, exercise_name):
        with self.connection:
            self.cursor.execute("SELECT * FROM exercises WHERE LOWER(exercise_name) = LOWER(?)", (exercise_name,))
            return self.cursor.fetchall()

    def update_exercise(self, exercise_id, updated_values):
        table_name = 'exercises'

        if exercise_id.startswith('C'):
            set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
            sql = f"UPDATE {table_name} SET {set_clause} WHERE exercise_id = :exercise_id"
            updated_values['exercise_id'] = exercise_id

            with self.connection:
                self.cursor.execute(sql, updated_values)
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

    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(exercise_id, 2) AS INTEGER)) FROM exercises WHERE exercise_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    def remove_exercise(self, exercise_id):
        with self.connection:
            if exercise_id.startswith('C'):
                self.cursor.execute("DELETE FROM exercises WHERE exercise_id=?", (exercise_id,))
            else:
                print("Cannot delete preset exercises.")

    def drop_exercise(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS exercises")

# db = LocalDB('local_db.db')
# exercise = Exercise(db.connection)
# exercise_data = ['-=', '07/02/2024']
# print(exercise.monthly_exercise_data('10', '2023'))
# exercise.remove_exercise(13)

# exercise.remove_exercise('C9')

# exercise_data = {
#     "exercise_name": 'Test 0',
#     "description": '',
#     "type": 'exercise_type',
#     "body_part": 'body_part',
#     "equipment": 'equipment',
#     "level": 'exercise_level',
#     "rating": '0',
#     "rating_description": 'fd',
#     "is_active": 1,
# }

# exercise.insert_exercise(exercise_data)
# value = exercise.get_exercise_by_name('Test 1')

# print(value[0][0])
# db.print_exercises()
# db.close_connection()