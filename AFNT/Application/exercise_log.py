import sqlite3
from local_db import LocalDB

"""
This class handles all database and other operations related to the `exercise_logs` table from LocalDB.
"""
class ExerciseLog():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    # Inserts exercise log data into the database
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

    # Function for allocating exercise log to a workout log 
    def allocate_exercise_logs(self, workout_log_id_to_copy, new_workout_log_id):
        try:
            # Fetch exercise logs with the specified workout log ID to copy
            self.cursor.execute("SELECT workout_log_id, exercise_id, sets, reps, weight_kg, rest_per_set_s, duration, distance_m, rpe, is_complete, date_complete, time_complete, details, is_active FROM exercise_logs WHERE workout_log_id = ?", (workout_log_id_to_copy,))
            exercise_logs_to_copy = self.cursor.fetchall()
            if exercise_logs_to_copy:
                for exercise_log in exercise_logs_to_copy:
                    exercise_log_data = list(exercise_log)
                    exercise_log_data[0] = new_workout_log_id  # Update workout_log_id
                    exercise_log_data[8] = ''  # rpe
                    exercise_log_data[9] = 0  # is_complete
                    exercise_log_data[10] = ''   # date_complete
                    exercise_log_data[11] = ''  # time_complete
                    exercise_log_data[12] = ''  # details
                    exercise_log_data[13] = 1   # is_active
                    
                    # Insert the modified exercise log into the table
                    self.insert_exercise_log(dict(zip(['workout_log_id', 'exercise_id', 'sets', 'reps', 'weight_kg', 'rest_per_set_s', 'duration', 'distance_m', 'rpe', 'is_complete', 'date_complete', 'time_complete', 'details', 'is_active'], exercise_log_data)))
                    
                self.connection.commit()
                return True
            else:
                return 0

        except sqlite3.Error as e:
            print("Error copying and updating exercise logs:", e)
            return False

    # Gets the exercise log fields using workout_log_id
    def get_exercise_log_by_workout_log_id(self, workout_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM exercise_logs WHERE workout_log_id=?", (workout_log_id,))
            return self.cursor.fetchall()

    # Gets the exercise_id of the selected exercise log using exercise_log_id
    def get_exercise_id(self, exercise_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM exercise_logs WHERE exercise_log_id=?", (exercise_log_id,))
            exercise_log_data = self.cursor.fetchall()
            return exercise_log_data[0][1]

    # Select the latest exercise log for the specified exercise_id
    def get_latest_exercise_log_by_exercise_id(self, exercise_id):
        try:
            with self.connection:
                self.cursor.execute("SELECT * FROM exercise_logs WHERE exercise_id=? LIMIT 1", (exercise_id,))
                latest_exercise_log = self.cursor.fetchone()
                return latest_exercise_log

        except sqlite3.Error as e:
            print("Error retrieving latest exercise log by exercise id:", e)
            return None

    # Gets the defined columns of the selected exercise logs using workout_log_id 
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
                        el.is_active = 1;
                """, (workout_log_id,))
                return self.cursor.fetchall()

        except Exception as e:
            print(f"Error retrieving exercise logs details: {e}")
            return []

    # Gets all the exercise logs using columns from both exercise_logs and exercise tables
    def get_all_exercise_logs_details(self):
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
                        el.duration,
                        el.distance_m
                    FROM 
                        exercise_logs AS el
                    JOIN 
                        exercises AS e ON el.exercise_id = e.exercise_id
                    WHERE 
                        el.is_active = 1;
                """)
                return self.cursor.fetchall()

        except Exception as e:
            print(f"Error retrieving exercise logs details: {e}")
            return []

    # Function for updating exercise_logs using the exercise_log_id and updating the values using the `updated_values` dictionary
    def update_exercise_log(self, exercise_log_id, updated_values):
        table_name = 'exercise_logs'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE exercise_log_id = :exercise_log_id"
        updated_values['exercise_log_id'] = exercise_log_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    # Function for removing the exercise log by setting `is_active` field to `0`. The database will only display those records with is_active = 1
    def remove_exercise_log(self, exercise_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE exercise_logs SET is_active = 0 WHERE exercise_log_id=?", (exercise_log_id,))
        except Exception as e:
            print(f"Error removing exercise log: {e}")

    # Function to readd the removed exercise log by setting its is_active to 1.
    def re_add_exercise_log(self, exercise_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE exercise_logs SET is_active = 1 WHERE exercise_log_id=?", (exercise_log_id,))
        except Exception as e:
            print(f"Error removing exercise log: {e}")

    # Drop the exercise_logs table from LocalDB
    def drop_exercise_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS exercise_logs")
