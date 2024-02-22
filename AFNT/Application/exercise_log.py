from datetime import datetime
import sqlite3
from local_db import LocalDB

class ExerciseLog():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_exercise_log(self, exercise_log):
        try:
            with self.connection:
                columns = ', '.join(exercise_log.keys())
                values = [exercise_log.get(key, '') for key in exercise_log.keys()]
                placeholders = ', '.join('?' for _ in exercise_log.values())

                sql = f"""
                    INSERT INTO exercise_logs 
                    ({columns}) 
                    VALUES ({placeholders})
                """
                self.cursor.execute(sql, values)

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid exercise_id or workout_log_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting exercise log: {e}")

    def get_exercise_log_by_id(self, exercise_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM exercise_logs WHERE exercise_log_id=?", (exercise_log_id,))
            return self.cursor.fetchall()

    def get_exercise_log_by_workout_log_id(self, workout_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM exercise_logs WHERE workout_log_id=?", (workout_log_id,))
            return self.cursor.fetchall()

    def get_exercise_logs_details(self, workout_log_id):
        try:
            with self.connection:
                self.cursor.execute("""
                    SELECT 
                        el.exercise_log_id,
                        e.exercise_name,
                        el.sets,
                        el.reps,
                        el.weight_kg,
                        el.rest_per_set_s,
                        el.distance_m,
                        el.rpe,
                        CASE 
                            WHEN el.is_complete = 1 THEN 'Yes' 
                            ELSE 'No' 
                        END AS is_complete
                    FROM 
                        exercise_logs AS el
                    JOIN 
                        exercises AS e ON el.exercise_id = e.exercise_id
                    WHERE 
                        el.workout_log_id = ? AND
                        el.is_active = 1;  -- Add condition for is_active field
                """, (workout_log_id,))
                return self.cursor.fetchall()

        except Exception as e:
            print(f"Error retrieving exercise logs details: {e}")
            return []

    def update_exercise_log(self, exercise_log_id, updated_values):
        table_name = 'exercise_logs'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE exercise_log_id = :exercise_log_id"
        updated_values['exercise_log_id'] = exercise_log_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    def remove_exercise_log(self, exercise_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE exercise_logs SET is_active = 0 WHERE exercise_log_id=?", (exercise_log_id,))
        except Exception as e:
            print(f"Error removing exercise log: {e}")

    def re_add_exercise_log(self, exercise_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE exercise_logs SET is_active = 1 WHERE exercise_log_id=?", (exercise_log_id,))
        except Exception as e:
            print(f"Error removing exercise log: {e}")

    def drop_exercise_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS exercise_logs")

db = LocalDB('local_db.db')
exercise_log = ExerciseLog(db.connection)

# exercise_log_data = ['-=', '07/02/2024']
# print(exercise_log.monthly_exercise_log_data('10', '2023'))
# exercise_log.remove_exercise_log(13)

# print(exercise_log.get_exercise_logs_details(2))
# exercise_log.remove_exercise_log(1)
# exercise_log.re_add_exercise_log(1)

# db.print_exercise_logs()
db.close_connection()
