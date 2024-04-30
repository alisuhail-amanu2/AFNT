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
            self.cursor.execute("UPDATE meal_logs SET is_active = 0 WHERE meal_log_id=?", (meal_log_id,))

    # Function to readd the removed meal log by setting its is_active to 1.
    def re_add_meal_log(self, meal_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE meal_logs SET is_active = 1 WHERE meal_log_id=?", (meal_log_id,))
        except Exception as e:
            print(f"Error removing meal log: {e}")

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
                        wl.energy_tot_kcal,
                        wl.protein_tot_g,
                        wl.lipid_tot_g,
                        wl.carbs_tot_g,
                        wl.sugar_tot_g,
                        wl.fiber_tot_g,
                        wl.iron_tot_mg,
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
                    log_date = datetime.strptime(log[9], "%d/%m/%Y")
                    if (not from_date or log_date >= from_date) and (not to_date or log_date <= to_date):
                        filtered_logs.append(log)
                
                return filtered_logs

        except Exception as e:
            print(f"Error retrieving meal logs: {e}")
            return []
    
    def get_all_meal_logs(self):
        try:
            with self.connection:
                query = """SELECT * FROM meal_logs"""
                self.cursor.execute(query)
                meal_logs = self.cursor.fetchall()
                return meal_logs

        except Exception as e:
            print(f"Error retrieving meal logs: {e}")
            return []

    def calculate_nutrients(self, meal_log_id):
        try:
            with self.connection:
                query = """
                        SELECT 
                            ROUND(SUM(fi.energy_kcal * fil.serving)) AS total_energy_kcal,
                            ROUND(SUM(fi.protein_g * fil.serving), 1) AS total_protein_g,
                            ROUND(SUM(fi.lipid_g * fil.serving), 1) AS total_fats_g,
                            ROUND(SUM(fi.carbs_g * fil.serving), 1) AS total_carbs_g,
                            ROUND(SUM(fi.fiber_td_g * fil.serving), 1) AS total_fiber_td_g,
                            ROUND(SUM(fi.sugar_g * fil.serving), 1) AS total_sugar_g,
                            ROUND(SUM(fi.calcium_mg * fil.serving), 1) AS total_calcium_mg,
                            ROUND(SUM(fi.iron_mg * fil.serving), 1) AS total_iron_mg
                        FROM 
                            food_item_logs AS fil
                        JOIN 
                            food_items AS fi ON fil.food_item_id = fi.food_item_id
                        WHERE 
                            fil.meal_log_id = ?
                        """
                self.cursor.execute(query, (meal_log_id,))
                result = self.cursor.fetchone()

                if result:
                    # Construct the dictionary
                    nutrients = {
                        'energy_tot_kcal': result[0],
                        'protein_tot_g': result[1],
                        'lipid_tot_g': result[2],
                        'carbs_tot_g': result[3],
                        'fiber_tot_g': result[4],
                        'sugar_tot_g': result[5],
                        'calcium_tot_mg': result[6],
                        'iron_tot_mg': result[7],
                    }
                    return nutrients
                else:
                    return None

        except Exception as e:
            print(f"Error calculating nutrients: {e}")
            return None



# connection = sqlite3.connect('local_db.db')
# meal_log = MealLog(connection)

# print(meal_log.calculate_nutrients(2))

# print(meal_log.get_date_selected_meal_logs('20/07/2023', '01/05/2024'))

# # print(meal_log.get_all_meal_logs())

# # meal_log.re_add_meal_log('C1')
# # print(meal_log.get_meal_log_by_id('C'))