from local_db import LocalDB
from datetime import datetime
import re

import sqlite3

class StepCount():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_step_count(self, step_count, selected_date):
        try:
            current_time = datetime.now().strftime('%H:%M:%S')

            with self.connection:
                self.cursor.execute("SELECT * FROM step_count WHERE date_recorded = ?", (selected_date,))
                existing_step_count = self.cursor.fetchone()

                if existing_step_count:
                    sql = """
                        UPDATE step_count 
                        SET step = ?, time_recorded = ?
                        WHERE date_recorded = ?
                    """
                    self.cursor.execute(sql, (step_count, current_time, selected_date))
                else:
                    sql = """
                        INSERT INTO step_count (step, date_recorded, time_recorded)
                        VALUES (?, ?, ?)
                    """
                    self.cursor.execute(sql, (step_count, selected_date, current_time))

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid workout_id or step_count_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting step_count data: {e}")

    def verify_step_count(self, step_count):
        if not step_count:
            return 31  # empty step_count

        try:
            step_count_int = int(step_count)
            return 32  # valid step_count
        except ValueError:
            return 33  # step_count contains invalid characters

    def delete_step_count(self):
        pass

    def monthy_step_count_data(self, selected_month, selected_year):
        days_in_month = 31
        if selected_month in [4, 6, 9, 11]:
            days_in_month = 30
        elif selected_month == 2:
            days_in_month = 29 if (selected_year % 4 == 0 and selected_year % 100 != 0) or (selected_year % 400 == 0) else 28

        days_of_month = list(range(1, days_in_month + 1))
        sql = "SELECT step, date_recorded FROM step_count WHERE SUBSTR(date_recorded, 4, 2) = ? AND SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_month).zfill(2), str(selected_year)))
        step_count_data = self.cursor.fetchall()

        # Sort the step_count data by date in ascending order
        step_count_data_sorted = sorted(step_count_data, key=lambda x: x[1])

        dates = []
        step_counts = []

        for data in step_count_data_sorted:
            day = int(data[1].split('/')[0])
            step = data[0]
            dates.append(day)
            step_counts.append(step)

        return [dates, step_counts, days_of_month]

    def yearly_step_count_data(self, selected_year):
        sql = "SELECT step, date_recorded FROM step_count WHERE SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_year),))
        step_count_data = self.cursor.fetchall()

        monthly_totals = {month: 0 for month in range(1, 13)}
        monthly_counts = {month: 0 for month in range(1, 13)}

        for data in step_count_data:
            month = int(data[1].split('/')[1])
            step = data[0]
            monthly_totals[month] += step
            monthly_counts[month] += 1

        monthly_averages = {month: monthly_totals[month] / monthly_counts[month] if monthly_counts[month] != 0 else 0 for month in range(1, 13)}
        months = list(monthly_averages.keys())
        averages = list(monthly_averages.values())

        return [months, averages]


# db = LocalDB('local_db.db')

# step = StepCount(db.connection)
# step_data = ['6500', '07/02/2024']
# print(step.verify_step_count('4,455'))
# step.insert_step_count('6500', '07/02/2024')
# print(step.monthy_step_count_data(10, 2023))

# db.print_step_count()
# db.close_connection()