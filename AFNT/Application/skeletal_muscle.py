from datetime import datetime
import sqlite3
from local_db import LocalDB
import matplotlib.pyplot as plt

"""
This class handles all database and other operations related to the `skeletal_muscle` table from LocalDB.
"""
class SkeletalMuscle():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    # Inserts skeletal_muscle (kg) record into the database with the current date and time
    def insert_skeletal_muscle(self, skeletal_muscle, selected_date):
        try:
            current_time = datetime.now().strftime('%H:%M:%S')

            with self.connection:
                self.cursor.execute("SELECT * FROM skeletal_muscle WHERE date_recorded = ?", (selected_date,))
                existing_skeletal_muscle = self.cursor.fetchone()

                if existing_skeletal_muscle:
                    sql = """
                        UPDATE skeletal_muscle 
                        SET skeletal_muscle_kg = ?, time_recorded = ?
                        WHERE date_recorded = ?
                    """
                    self.cursor.execute(sql, (skeletal_muscle, current_time, selected_date))
                else:
                    sql = """
                        INSERT INTO skeletal_muscle (skeletal_muscle_kg, date_recorded, time_recorded)
                        VALUES (?, ?, ?)
                    """
                    self.cursor.execute(sql, (skeletal_muscle, selected_date, current_time))

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid workout_id or skeletal_muscle_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting skeletal_muscle data: {e}")

    # Gets the skeletal muscle record by skeletal_muscle_id
    def get_skeletal_muscle_by_id(self, skeletal_muscle_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM skeletal_muscle WHERE skeletal_muscle_id=?", (skeletal_muscle_id,))
            return self.cursor.fetchall()

    # Updates skeletal muscle record using skeletal_muscle_id and updating the values using `updated_values` dictionary 
    def update_skeletal_muscle(self, skeletal_muscle_id, updated_values):
        table_name = 'skeletal_muscle'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE skeletal_muscle_id = :skeletal_muscle_id"
        updated_values['skeletal_muscle_id'] = skeletal_muscle_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    # Removes the skeletal muscle record using skeletal_muscle_id from the database
    def remove_skeletal_muscle(self, skeletal_muscle_id):
        with self.connection:
            self.cursor.execute("DELETE FROM skeletal_muscle WHERE skeletal_muscle_id=?", (skeletal_muscle_id,))

    # Drops the skeletal_muscle table from LocalDB
    def drop_skeletal_muscle(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS skeletal_muscle")

    # Verifys the skeletal_muscle value entered by user
    def verify_skeletal_muscle(self, skeletal_muscle):
        if not skeletal_muscle:
            return 27  # empty skeletal_muscle
        try:
            skeletal_muscle_float = float(skeletal_muscle) # Convert skeletal_muscle data from string to float
            return 25  # valid skeletal_muscle
        except ValueError:
            return 26  # invalid skeletal muscle format

    # Gets the skeletal muscle data using the selected month and year parameters and returns the dates, skeletal muscle values and days of the selected month in a list format
    def monthly_skeletal_muscle_data(self, selected_month, selected_year):
        days_in_month = 31
        if selected_month in [4, 6, 9, 11]:
            days_in_month = 30
        elif selected_month == 2:
            days_in_month = 29 if (selected_year % 4 == 0 and selected_year % 100 != 0) or (selected_year % 400 == 0) else 28

        days_of_month = list(range(1, days_in_month + 1))
        sql = "SELECT skeletal_muscle_kg, date_recorded FROM skeletal_muscle WHERE SUBSTR(date_recorded, 4, 2) = ? AND SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_month).zfill(2), str(selected_year)))
        skeletal_data = self.cursor.fetchall()

        # Sort the skeletal_muscle data by date in ascending order
        skeletal_data_sorted = sorted(skeletal_data, key=lambda x: x[1])

        dates = []
        skeletal_muscles = []

        for data in skeletal_data_sorted:
            day = int(data[1].split('/')[0])
            skeletal_muscle_kg = data[0]
            dates.append(day)
            skeletal_muscles.append(skeletal_muscle_kg)

        return [dates, skeletal_muscles, days_of_month]
  
    # Gets the skeletal muscle data using the selected year parameter and returns the months, average skeletal muscle values and calendar data in a list format
    def yearly_skeletal_muscle_data(self, selected_year):
        sql = "SELECT skeletal_muscle_kg, date_recorded FROM skeletal_muscle WHERE SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_year),))
        skeletal_data = self.cursor.fetchall()

        monthly_totals = {month: 0 for month in range(1, 13)}
        monthly_counts = {month: 0 for month in range(1, 13)}

        for data in skeletal_data:
            month = int(data[1].split('/')[1])
            skeletal_muscle_kg = data[0]
            monthly_totals[month] += skeletal_muscle_kg
            monthly_counts[month] += 1

        monthly_averages = {month: monthly_totals[month] / monthly_counts[month] if monthly_counts[month] != 0 else 0 for month in range(1, 13)}
        months = list(monthly_averages.keys())
        averages = list(monthly_averages.values())

        return [months, averages]
