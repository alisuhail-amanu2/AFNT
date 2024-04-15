from datetime import datetime
import sqlite3
from local_db import LocalDB

"""
This class handles all database and other operations related to the `meal_logs` table from LocalDB.
"""
class MealLog():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    # Function for adding new meal log record into the database
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

    # Get meal log by meal_log_id
    def get_meal_log_by_id(self, meal_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM meal_logs WHERE meal_log_id=?", (meal_log_id,))
            return self.cursor.fetchall()

    # Update meal log record using meal_log_id and updating the values using `updated_values` dictionary 
    def update_meal_log(self, meal_log_id, updated_values):
        table_name = 'meal_logs'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE meal_log_id = :meal_log_id"
        updated_values['meal_log_id'] = meal_log_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    # Remove meal log from the database
    def remove_meal_log(self, meal_log_id):
        with self.connection:
            self.cursor.execute("DELETE FROM meal_logs WHERE meal_log_id=?", (meal_log_id,))

    # Drops the meal_logs table from LocalDB
    def drop_meal_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS meal_logs")

    # Get meal_log records using the from a selected date range. Also retrives columns from both meal and meal_logs tables and returns it in a list
    def get_date_selected_meal_logs(self, from_date, to_date):
        try:
            # Convert date strings to datetime objects
            from_date = datetime.strptime(from_date, "%d/%m/%Y") if from_date else None
            to_date = datetime.strptime(to_date, "%d/%m/%Y") if to_date else None

            with self.connection:
                # Use parameterized query to prevent SQL injection
                query = """
                    SELECT 
                        wl.meal_log_id,
                        w.description,
                        w.energy_tot_kcal,
                        w.serving,
                        w.protein_tot_g,
                        w.lipid_tot_g,
                        w.carbs_tot_g,
                        w.sugar_tot_g,
                        w.fiber_tot_g,
                        w.iron_tot_mg,
                        wl.date_ate,
                        wl.time_ate,
                        CASE 
                            WHEN wl.ate = 1 THEN 'Yes' 
                            ELSE 'No' 
                        END AS ate
                    FROM 
                        meal_logs AS wl
                    JOIN 
                        meals AS w ON wl.meal_id = w.meal_id
                    WHERE 
                        wl.is_active = 1
                """

                self.cursor.execute(query)
                meal_logs = self.cursor.fetchall()

                # Filter meal logs based on date range
                filtered_logs = []
                for log in meal_logs:
                    log_date = datetime.strptime(log[10], "%d/%m/%Y")
                    if (not from_date or log_date >= from_date) and (not to_date or log_date <= to_date):
                        filtered_logs.append(log)
                
                return filtered_logs

        except Exception as e:
            print(f"Error retrieving meal logs: {e}")
            return []
