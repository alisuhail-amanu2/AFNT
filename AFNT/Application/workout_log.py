from datetime import datetime
import sqlite3
from local_db import LocalDB

"""
This class handles all database and other operations related to the `workout_logs` table from LocalDB.
"""
class WorkoutLog():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    # Inserts the new workout log into the database
    def insert_workout_log(self, workout_log):
        try:
            with self.connection:
                # Check if there are already 3 workout logs for the same date_assigned and is_active is 1
                self.cursor.execute("SELECT COUNT(*) FROM workout_logs WHERE date_assigned = ? AND is_active = 1", (workout_log['date_assigned'],))
                count = self.cursor.fetchone()[0]
                if count >= 3:
                    print("Error: Cannot add more than 3 active workout logs on the same day.")
                    return None

                columns = ', '.join(workout_log.keys())
                values = [workout_log.get(key, '') for key in workout_log.keys()]
                placeholders = ', '.join('?' for _ in workout_log.values())

                sql = f"""
                    INSERT INTO workout_logs 
                    ({columns}) 
                    VALUES ({placeholders})
                """
                self.cursor.execute(sql, values)
                # Retrieve the last inserted row id, which is the workout_log_id
                workout_log_id = self.cursor.lastrowid
                return workout_log_id

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid workout_id or workout_log_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting workout log: {e}")

    # Gets the workout_log_id by latest date, using workout_id
    def get_latest_workout_log_id(self, workout_id):
        try:
            with self.connection:
                self.cursor.execute("SELECT workout_log_id FROM workout_logs WHERE workout_id = ? ORDER BY date_assigned DESC LIMIT 1", (workout_id,))
                latest_workout_log_id = self.cursor.fetchone()
                if latest_workout_log_id:
                    return latest_workout_log_id[0]
                else:
                    print("No workout logs found for the specified workout_id.")
                    return None

        except sqlite3.Error as e:
            print("Error retrieving latest workout log id:", e)
            return None

    # Gets workout log record by workout_log_id
    def get_workout_log_by_id(self, workout_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM workout_logs WHERE workout_log_id=?", (workout_log_id,))
            return self.cursor.fetchall()

    # Gets the workout log record by workout_id
    def get_workout_logs_by_workout_id(self, workout_id):
        try:
            with self.connection:
                self.cursor.execute("SELECT * FROM workout_logs WHERE workout_id = ?", (workout_id,))
                workout_logs = self.cursor.fetchall()
                return workout_logs

        except sqlite3.Error as e:
            print("Error retrieving workout logs by workout id:", e)
            return None

    # Gets all workout log data
    def get_all_workout_logs(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM workout_logs")
            return self.cursor.fetchall()

    # Gets workout log details using fields from both workouts and workout_logs table
    def get_workout_logs_details(self):
        try:
            with self.connection:
                self.cursor.execute("""
                    SELECT 
                        wl.workout_log_id,
                        w.workout_name,
                        wl.date_assigned,
                        wl.time_assigned,
                        CASE 
                            WHEN wl.is_complete = 1 THEN 'Yes' 
                            ELSE 'No' 
                        END AS is_complete
                    FROM 
                        workout_logs AS wl
                    JOIN 
                        workouts AS w ON wl.workout_id = w.workout_id;
                """)
                return self.cursor.fetchall()

        except Exception as e:
            print(f"Error retrieving workout logs details: {e}")

    # Gets workout logs from a date range
    def get_date_selected_workout_logs(self, from_date, to_date):
        try:
            with self.connection:
                self.cursor.execute("""
                    SELECT 
                        wl.workout_log_id,
                        w.workout_name,
                        wl.date_assigned,
                        wl.time_assigned,
                        CASE 
                            WHEN wl.is_complete = 1 THEN 'Yes' 
                            ELSE 'No' 
                        END AS is_complete
                    FROM 
                        workout_logs AS wl
                    JOIN 
                        workouts AS w ON wl.workout_id = w.workout_id
                    WHERE 
                        wl.is_active = 1;
                """)
                workout_logs = self.cursor.fetchall()
                
                # Filter workout logs based on date range
                from_date = datetime.strptime(from_date, "%d/%m/%Y") if from_date else None
                to_date = datetime.strptime(to_date, "%d/%m/%Y") if to_date else None
                
                filtered_logs = []
                for log in workout_logs:
                    log_date = datetime.strptime(log[2], "%d/%m/%Y")
                    if (not from_date or log_date >= from_date) and (not to_date or log_date <= to_date):
                        filtered_logs.append(log)
                
                return filtered_logs

        except Exception as e:
            print(f"Error retrieving workout logs: {e}")
            return []

    # Updates workout log using workout_log_id and updating the values by passing the changed parameters.
    def update_workout_log(self, workout_log_id, date_assigned, time_assigned, is_complete):
        try:
            with self.connection:
                sql = """
                    UPDATE workout_logs 
                    SET date_assigned = ?,
                        time_assigned = ?,
                        is_complete = ?
                    WHERE workout_log_id = ?
                """
                self.cursor.execute(sql, (date_assigned, time_assigned, is_complete, workout_log_id))

        except Exception as e:
            print(f"Error updating workout log fields: {e}")

    # Function for removing the workout log by setting `is_active` field to `0`. The database will only display those records with is_active = 1
    def remove_workout_log(self, workout_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE workout_logs SET is_active = 0 WHERE workout_log_id=?", (workout_log_id,))
        except Exception as e:
            print(f"Error removing workout log: {e}")

    # Function to readd the removed workout log by setting its is_active to 1.
    def re_add_workout_log(self, workout_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE workout_logs SET is_active = 1 WHERE workout_log_id=?", (workout_log_id,))
        except Exception as e:
            print(f"Error removing workout log: {e}")

    # Drops the workout_logs table from LocalDB
    def drop_workout_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS workout_logs")
