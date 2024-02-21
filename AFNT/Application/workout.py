from datetime import datetime
import sqlite3
from local_db import LocalDB

class Workout():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_workout(self, workout):
        try:
            table_name = 'workouts'
            with self.connection:
                self.cursor.execute(f"SELECT MAX(workout_id) FROM {table_name} WHERE workout_id LIKE 'C%'")
                latest_id = self.cursor.fetchone()[0]

            new_id_numeric = int(latest_id[1:]) + 1 if latest_id else 1
            new_id = f'C{new_id_numeric}'

            workout['workout_id'] = new_id

            columns = ', '.join(key for key in workout.keys())
            placeholders = ', '.join(':' + key for key in workout.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.connection:
                self.cursor.execute(sql, workout)

        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting workout: {e}")

    def get_workout_by_id(self, workout_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM workouts WHERE workout_id=?", (workout_id,))
            return self.cursor.fetchall()

    def get_workout_by_name(self, workout_name):
        with self.connection:
            self.cursor.execute("SELECT * FROM workouts WHERE LOWER(workout_name) = LOWER(?)", (workout_name,))
            return self.cursor.fetchall()

    def update_workout(self, workout_id, updated_values):
        table_name = 'workouts'

        # Check if the workout_id is a custom ID (starts with 'C')
        if workout_id.startswith('C'):
            # If it's a custom ID, update the existing record
            set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
            sql = f"UPDATE {table_name} SET {set_clause} WHERE workout_id = :workout_id"
            updated_values['workout_id'] = workout_id

            with self.connection:
                self.cursor.execute(sql, updated_values)
        else:
            # If it's a preset ID, create a copy with a custom ID and update the copy
            # Assume workout_id is numeric for preset IDs
            with self.connection:
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()
                columns = [column_info[1] for column_info in columns_info]

                self.cursor.execute(f"SELECT * FROM {table_name} WHERE workout_id = ?", (workout_id,))
                existing_record = self.cursor.fetchone()

                if existing_record:
                    # Create a copy with a custom ID (C ID)
                    new_id_numeric = self._get_next_custom_id_numeric()
                    new_id = f'C{new_id_numeric}'

                    # Copy values and update with user-provided values
                    updated_record = dict(zip(columns, existing_record))
                    updated_record.update(updated_values)
                    updated_record['workout_id'] = new_id

                    # Insert the updated record with the custom ID
                    columns = ', '.join(key for key in updated_record.keys())
                    placeholders = ', '.join(':' + key for key in updated_record.keys())
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    self.cursor.execute(insert_sql, updated_record)

    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(workout_id, 2) AS INTEGER)) FROM workouts WHERE workout_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    def remove_workout(self, workout_id):
        with self.connection:
            if workout_id.startswith('C'):
                self.cursor.execute("DELETE FROM workouts WHERE workout_id=?", (workout_id,))
            else:
                print("Cannot delete preset workouts.")

    def drop_workout(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS workouts")

# db = LocalDB('local_db.db')
# weight = Weight(db.connection)
# weight_data = ['-=', '07/02/2024']
# print(weight.monthly_weight_data('10', '2023'))
# weight.remove_weight(13)
# db.print_weight()
# db.close_connection()