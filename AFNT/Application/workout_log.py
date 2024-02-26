from datetime import datetime
import sqlite3
from local_db import LocalDB

class WorkoutLog():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_workout_log(self, workout_log):
        try:
            with self.connection:
                columns = ', '.join(workout_log.keys())
                values = [workout_log.get(key, '') for key in workout_log.keys()]
                placeholders = ', '.join('?' for _ in workout_log.values())

                sql = f"""
                    INSERT INTO workout_logs 
                    ({columns}) 
                    VALUES ({placeholders})
                """
                self.cursor.execute(sql, values)

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid workout_id or workout_log_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting workout log: {e}")

    def get_workout_log_by_id(self, workout_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM workout_logs WHERE workout_log_id=?", (workout_log_id,))
            return self.cursor.fetchall()

    def get_all_workout_logs(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM workout_logs")
            return self.cursor.fetchall()

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

    def remove_workout_log(self, workout_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE workout_logs SET is_active = 0 WHERE workout_log_id=?", (workout_log_id,))
        except Exception as e:
            print(f"Error removing workout log: {e}")

    def re_add_workout_log(self, workout_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE workout_logs SET is_active = 1 WHERE workout_log_id=?", (workout_log_id,))
        except Exception as e:
            print(f"Error removing workout log: {e}")

    def drop_workout_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS workout_logs")

# db = LocalDB('local_db.db')
# workout_log = WorkoutLog(db.connection)
# db.print_workout_logs()

# print("workout records", workout_log.get_workout_logs_details('01/10/2023', '01/01/2024'))
# print("workout records", workout_log.get_date_selected_workout_logs('01/02/2023', '28/02/2023'))
# workout_log.update_workout_log(6, '10/02/2024', '16:20:00', 0)
# workout_log.remove_workout_log(1)
# workout_log.re_add_workout_log(5)
# print(workout_log.get_workout_details())

# # db.print_workout_logs()
# db.close_connection()