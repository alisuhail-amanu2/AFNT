from datetime import datetime
import sqlite3
from local_db import LocalDB

"""
This class handles all database and other operations related to the `weight` table from LocalDB.
"""
class Weight():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
    
    # Inserts weight (kg) along with the current datetime into the database
    def insert_weight(self, weight, selected_date):
        try:
            current_time = datetime.now().strftime('%H:%M:%S')

            with self.connection:
                self.cursor.execute("SELECT * FROM weight WHERE date_recorded = ?", (selected_date,))
                existing_weight = self.cursor.fetchone()

                if existing_weight:
                    sql = """
                        UPDATE weight 
                        SET weight_kg = ?, time_recorded = ?
                        WHERE date_recorded = ?
                    """
                    self.cursor.execute(sql, (weight, current_time, selected_date))
                else:
                    sql = """
                        INSERT INTO weight (weight_kg, date_recorded, time_recorded)
                        VALUES (?, ?, ?)
                    """
                    self.cursor.execute(sql, (weight, selected_date, current_time))

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid workout_id or weight_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting weight data: {e}")

    # Gets weight record by weight_id
    def get_weight_by_id(self, weight_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM weight WHERE weight_id=?", (weight_id,))
            return self.cursor.fetchall()

    # Updates weight using weight_id and updating the values with the `updated_values` dictionary.
    def update_weight(self, weight_id, updated_values):
        table_name = 'weight'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE weight_id = :weight_id"
        updated_values['weight_id'] = weight_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    # Deletes weight record from the database
    def remove_weight(self, weight_id):
        with self.connection:
            self.cursor.execute("DELETE FROM weight WHERE weight_id=?", (weight_id,))

    # Drops weight table from LocalDB
    def drop_weight(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS weight")

    # Verifies weight entered by user
    def verify_weight(self, weight):
        if isinstance(weight, str):
            try:
                weight = float(weight)
            except ValueError:
                return 16  # Invalid weight format

        if not isinstance(weight, (int, float)) or weight < 20 or weight > 350:
            return 17  # Weight out of range
        try:
            weight = float(weight)
            if weight <= 0:
                return 18 # Weight is a negative number
        except ValueError:
            return 19 # Weight is a valid number or decimal
        
        return 20 # Weight data is valid
    
    # Gets the weight data using the selected month and year parameters and returns the dates, weight values and days of the selected month in a list format
    def monthly_weight_data(self, selected_month, selected_year):
        days_in_month = 31
        if selected_month in [4, 6, 9, 11]:
            days_in_month = 30
        elif selected_month == 2:
            days_in_month = 29 if (selected_year % 4 == 0 and selected_year % 100 != 0) or (selected_year % 400 == 0) else 28

        days_of_month = list(range(1, days_in_month + 1))
        sql = "SELECT weight_kg, date_recorded FROM weight WHERE SUBSTR(date_recorded, 4, 2) = ? AND SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_month).zfill(2), str(selected_year)))
        weight_data = self.cursor.fetchall()

        # Sort the weight data by date in ascending order
        weight_data_sorted = sorted(weight_data, key=lambda x: x[1])

        dates = []
        weights = []

        for data in weight_data_sorted:
            day = int(data[1].split('/')[0])
            weight_kg = data[0]
            dates.append(day)
            weights.append(weight_kg)

        return [dates, weights, days_of_month]
  
  # Gets the weight data using the selected year parameter and returns the months, average weight values and calendar data in a list format
    def yearly_weight_data(self, selected_year):
        sql = "SELECT weight_kg, date_recorded FROM weight WHERE SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_year),))
        weight_data = self.cursor.fetchall()

        monthly_totals = {month: 0 for month in range(1, 13)}
        monthly_counts = {month: 0 for month in range(1, 13)}

        for data in weight_data:
            month = int(data[1].split('/')[1])
            weight_kg = data[0]
            monthly_totals[month] += weight_kg
            monthly_counts[month] += 1

        monthly_averages = {month: monthly_totals[month] / monthly_counts[month] if monthly_counts[month] != 0 else 0 for month in range(1, 13)}
        months = list(monthly_averages.keys())
        averages = list(monthly_averages.values())

        return [months, averages]
