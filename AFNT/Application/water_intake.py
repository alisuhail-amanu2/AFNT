from datetime import datetime
import sqlite3
from local_db import LocalDB

"""
This class handles all database and other operations related to the `water_intake` table from LocalDB.
"""
class WaterIntake():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    # Inserts water intake (ml) along with the current datetime into the database
    def insert_water_intake(self, water_intake):
        try:
            with self.connection:
                columns = ', '.join(water_intake.keys())
                values = [water_intake.get(key, '') for key in water_intake.keys()]
                placeholders = ', '.join('?' for _ in water_intake.values())

                sql = f"""
                    INSERT INTO water_intake 
                    ({columns}) 
                    VALUES ({placeholders})
                """
                self.cursor.execute(sql, values)

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid workout_id or water_intake_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting water intake log: {e}")

    # Gets water intake record by water_intake_id
    def get_water_intake_by_id(self, water_intake_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM water_intake WHERE water_intake_id=?", (water_intake_id,))
            return self.cursor.fetchall()

    # Gets water intake record by selected date
    def get_water_intake_by_date(self, date_recorded):
        with self.connection:
            self.cursor.execute("SELECT * FROM water_intake WHERE date_recorded=?", (date_recorded,))
            return self.cursor.fetchall()

    # Updates water intake record using water_intake_id and updating the values with the `updated_values` dictionary.
    def update_water_intake(self, water_intake_id, updated_values):
        table_name = 'water_intake'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE water_intake_id = :water_intake_id"
        updated_values['water_intake_id'] = water_intake_id

        with self.connection:
            self.cursor.execute(sql, updated_values)
    
    # Gets all water intake records and returns it in a list
    def get_all_water_intake(self):
        water_intakes = []
        sql = "SELECT * FROM water_intake"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            water_intakes.append(row)
        return water_intakes

    # Deletes all water intake records
    def remove_all_water_intake(self):
        with self.connection:
            self.cursor.execute("DELETE FROM water_intake")

    # Drops the water_intake table from LocalDB
    def drop_water_intake(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS water_intake")

    # Verifies water intake input and the date selected by user
    def verify_water_intake(self, water_intake, date_recorded):
        water_intake_str = str(water_intake)

        if len(water_intake_str) > 5:
            return 11  # Error code for water intake length exceeds limit
        try:
            water_intake = int(water_intake)
        except ValueError:
            return 12  # Error code for invalid water intake format (non-integer)
        if water_intake <= 0:
            return 13  # Error code for no water intake provided
        if not date_recorded:
            return 14  # Error code for no date selected

        # Add current time
        time_recorded = datetime.now().strftime('%H:%M:%S')

        existing_records = self.get_water_intake_by_date(date_recorded)
        if existing_records:
            water_intake_id = existing_records[0][0]
            updated_values = {'water_intake_ml': water_intake, 'time_recorded': time_recorded}
            self.update_water_intake(water_intake_id, updated_values)
        else:
            new_water_intake = {'water_intake_ml': water_intake, 'date_recorded': date_recorded, 'time_recorded': time_recorded}
            self.insert_water_intake(new_water_intake)

        return 15  # Success code

    # Gets the water intake data using the selected month and year parameters and returns the dates, water intake values and days of the selected month in a list format
    def monthly_water_intake_data(self, selected_month, selected_year):
        days_in_month = 31
        if selected_month in [4, 6, 9, 11]:
            days_in_month = 30
        elif selected_month == 2:
            days_in_month = 29 if (selected_year % 4 == 0 and selected_year % 100 != 0) or (selected_year % 400 == 0) else 28

        days_of_month = list(range(1, days_in_month + 1))
        sql = "SELECT water_intake_ml, date_recorded FROM water_intake WHERE SUBSTR(date_recorded, 4, 2) = ? AND SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_month).zfill(2), str(selected_year)))
        water_intake_data = self.cursor.fetchall()

        dates = []
        water_intakes = []

        for data in water_intake_data:
            day = int(data[1].split('/')[0])
            water_intake_ml = data[0]
            dates.append(day)
            water_intakes.append(water_intake_ml)

        data = [dates, water_intakes, days_of_month]
        return data

# Gets the water intake data using the selected year parameter and returns the months, average water intake values and calendar data in a list format
    def yearly_water_intake_graph(self, selected_year):
        sql = "SELECT water_intake_ml, date_recorded FROM water_intake WHERE SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_year),))
        water_intake_data = self.cursor.fetchall()

        monthly_totals = {month: 0 for month in range(1, 13)}
        monthly_counts = {month: 0 for month in range(1, 13)}

        for data in water_intake_data:
            month = int(data[1].split('/')[1])
            water_intake_ml = data[0]
            monthly_totals[month] += water_intake_ml
            monthly_counts[month] += 1

        monthly_averages = {month: monthly_totals[month] / monthly_counts[month] if monthly_counts[month] != 0 else 0 for month in range(1, 13)}
        data = [monthly_averages.keys(), monthly_averages.values()]
        return data
