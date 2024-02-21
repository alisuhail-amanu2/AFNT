from datetime import datetime
import sqlite3
from local_db import LocalDB

class Exercise():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_exercise(self, exercise):
        try:
            table_name = 'exercises'
            with self.connection:
                self.cursor.execute(f"SELECT MAX(exercise_id) FROM {table_name} WHERE exercise_id LIKE 'C%'")
                latest_id = self.cursor.fetchone()[0]

            new_id_numeric = int(latest_id[1:]) + 1 if latest_id else 1
            new_id = f'C{new_id_numeric}'

            exercise['exercise_id'] = new_id

            columns = ', '.join(key for key in exercise.keys())
            placeholders = ', '.join(':' + key for key in exercise.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.connection:
                self.cursor.execute(sql, exercise)

        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")

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

        # Check if the exercise_id is a custom ID (starts with 'C')
        if exercise_id.startswith('C'):
            # If it's a custom ID, update the existing record
            set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
            sql = f"UPDATE {table_name} SET {set_clause} WHERE exercise_id = :exercise_id"
            updated_values['exercise_id'] = exercise_id

            with self.connection:
                self.cursor.execute(sql, updated_values)
        else:
            # If it's a preset ID, create a copy with a custom ID and update the copy
            # Assume exercise_id is numeric for preset IDs
            with self.connection:
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()
                columns = [column_info[1] for column_info in columns_info]

                self.cursor.execute(f"SELECT * FROM {table_name} WHERE exercise_id = ?", (exercise_id,))
                existing_record = self.cursor.fetchone()

                if existing_record:
                    # Create a copy with a custom ID (C ID)
                    new_id_numeric = self._get_next_custom_id_numeric()
                    new_id = f'C{new_id_numeric}'

                    # Copy values and update with user-provided values
                    updated_record = dict(zip(columns, existing_record))
                    updated_record.update(updated_values)
                    updated_record['exercise_id'] = new_id

                    # Insert the updated record with the custom ID
                    columns = ', '.join(key for key in updated_record.keys())
                    placeholders = ', '.join(':' + key for key in updated_record.keys())
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    self.cursor.execute(insert_sql, updated_record)

    def _get_next_custom_id_numeric(self):
        # Get the next available numeric part for the custom ID
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
# weight = Weight(db.connection)
# weight_data = ['-=', '07/02/2024']
# print(weight.monthly_weight_data('10', '2023'))
# weight.remove_weight(13)
# db.print_weight()
# db.close_connection()