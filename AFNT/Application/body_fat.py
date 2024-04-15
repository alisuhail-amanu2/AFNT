import sqlite3
from datetime import date, time, datetime
from local_db import LocalDB
from user import User
from bmi import BMI
import calendar

"""
This class handles all database and other operations related to the `body_fat` table from LocalDB.
"""
class BodyFat():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    # This function calculates the body fat using the weight, age and gender and inserts it in the database using `insert_body_fat` function
    def calculate_body_fat(self, weight, username, selected_date):
        user = User()
        db = LocalDB('local_db.db')
        bmi_table = BMI(db.connection)

        bmi = bmi_table.get_most_recent_bmi()
        age = user.get_user_age(username)
        gender = user.get_user_gender(username)

        if gender == 'Male':
            body_fat = round((1.20 * bmi) + 0.23 * age - 16.2, 1)
            self.insert_body_fat(weight, body_fat, selected_date)
        elif gender == 'Female':
            body_fat = round((1.20 * bmi) + 0.23 * age - 5.4, 1)
            self.insert_body_fat(weight, body_fat, selected_date)

    # Inserts body fat value (kg and percent) with the current datetime into the database 
    def insert_body_fat(self, weight, body_fat_kg, selected_date):
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            body_fat_percent = round((body_fat_kg / weight) * 100, 1) # Calculate body fat percentage

            with self.connection:
                self.cursor.execute("SELECT * FROM body_fat WHERE date_recorded = ?", (selected_date,))
                existing_body_fat = self.cursor.fetchone()

                if existing_body_fat:
                    sql = """
                        UPDATE body_fat 
                        SET body_fat_kg = ?, body_fat_percent = ?, time_recorded = ?
                        WHERE date_recorded = ?
                    """
                    self.cursor.execute(sql, (body_fat_kg, body_fat_percent, current_time, selected_date))
                else:
                    sql = """
                        INSERT INTO body_fat (body_fat_kg, body_fat_percent, date_recorded, time_recorded)
                        VALUES (?, ?, ?, ?)
                    """
                    self.cursor.execute(sql, (body_fat_kg, body_fat_percent, selected_date, current_time))

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid workout_id or body_fat_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting body_fat data: {e}")

    # Gets body fat record using body_fat_id
    def get_body_fat_by_id(self, body_fat_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM body_fat WHERE body_fat_id=?", (body_fat_id,))
            return self.cursor.fetchall()

    # Updates body fat using body_fat_id and updating the values with the `updated_values` dictionary.
    def update_body_fat(self, body_fat_id, updated_values):
        table_name = 'body_fat'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE body_fat_id = :body_fat_id"
        updated_values['body_fat_id'] = body_fat_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    # Removes the body fat record from the database using body_fat_id
    def remove_body_fat(self, body_fat_id):
        with self.connection:
            self.cursor.execute("DELETE FROM body_fat WHERE body_fat_id=?", (body_fat_id,))

    # Drops body fat table from LocalDB
    def drop_body_fat(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS body_fat")

    # Verify body fat data entered manually by user
    def verify_body_fat(self, body_fat):
        if not body_fat:
            return 30  # empty body_fat
        try:
            body_fat_float = float(body_fat) # Convert body_fat data from string to float
            return 28  # valid body_fat
        except ValueError:
            return 29  # Invalid body fat value format

    # Gets the body fat data using the selected month and year parameters and returns the dates, body fat values and days of the selected month in a list format
    def monthly_body_fat_data(self, selected_month, selected_year):
        days_in_month = calendar.monthrange(selected_year, selected_month)[1]
        days_of_month = list(range(1, days_in_month + 1))

        sql = "SELECT body_fat_percent, date_recorded FROM body_fat WHERE SUBSTR(date_recorded, 4, 2) = ? AND SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_month).zfill(2), str(selected_year)))
        body_fat_data = self.cursor.fetchall()

        dates = []
        body_fats = []

        for data in body_fat_data:
            day = int(data[1].split('/')[0])
            body_fat = data[0]
            dates.append(day)
            body_fats.append(body_fat)
        
        return [dates, body_fats, days_of_month]

    # Gets the body fat data using the selected year parameter and returns the months, average body fat values and calendar data in a list format
    def yearly_body_fat_data(self, selected_year):
        months = list(range(1, 13))
        avg_body_fat_values = []
        for month in months:
            sql = "SELECT body_fat_percent FROM body_fat WHERE SUBSTR(date_recorded, 4, 2) = ? AND SUBSTR(date_recorded, 7, 4) = ?"
            self.cursor.execute(sql, (str(month).zfill(2), str(selected_year)))
            body_fat_data = self.cursor.fetchall()

            avg_body_fat = sum(body_fat[0] for body_fat in body_fat_data) / len(body_fat_data) if body_fat_data else 0
            avg_body_fat_values.append(avg_body_fat)
        
        return [months, avg_body_fat_values, calendar.month_abbr[1:]]
