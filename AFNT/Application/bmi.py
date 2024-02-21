from datetime import datetime
import sqlite3
from local_db import LocalDB
import matplotlib.pyplot as plt
import calendar

class BMI():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def get_most_recent_bmi(self):
        try:
            with self.connection:
                self.cursor.execute("SELECT bmi FROM bmi ORDER BY SUBSTR(date_recorded, 7, 4)||'-'||SUBSTR(date_recorded, 4, 2)||'-'||SUBSTR(date_recorded, 1, 2) DESC LIMIT 1")
                most_recent_bmi = self.cursor.fetchone()
                if most_recent_bmi:
                    return most_recent_bmi[0]
                else:
                    return 0
        except Exception as e:
            print(f"Error fetching most recent bmi data: {e}")
            return 0

    def calculate_bmi(self, weight, height):
        return round(weight / ((height/100) * (height/100)), 1)

    def insert_bmi(self, weight, height, selected_date):
        try:
            bmi = self.calculate_bmi(weight, height)
            current_time = datetime.now().strftime('%H:%M:%S')

            with self.connection:
                self.cursor.execute("SELECT bmi_id FROM bmi WHERE date_recorded=?", (selected_date,))
                existing_bmi_id = self.cursor.fetchone()

                if existing_bmi_id:
                    sql_update = """
                        UPDATE bmi 
                        SET bmi = ?, time_recorded = ?
                        WHERE bmi_id = ?
                    """
                    self.cursor.execute(sql_update, (bmi, current_time, existing_bmi_id[0]))
                else:
                    sql_insert = """
                        INSERT INTO bmi (bmi, date_recorded, time_recorded)
                        VALUES (?, ?, ?)
                    """
                    self.cursor.execute(sql_insert, (bmi, selected_date, current_time))

        except Exception as e:
            print(f"Error inserting BMI data: {e}")

    def get_bmi_by_id(self, bmi_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM bmi WHERE bmi_id=?", (bmi_id,))
            return self.cursor.fetchall()

    def update_bmi(self, bmi_id, updated_values):
        table_name = 'bmi'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE bmi_id = :bmi_id"
        updated_values['bmi_id'] = bmi_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    def remove_bmi(self, bmi_id):
        with self.connection:
            self.cursor.execute("DELETE FROM bmi WHERE bmi_id=?", (bmi_id,))

    def drop_bmi(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS bmi")

    def monthly_bmi_data(self, selected_month, selected_year):
        days_in_month = calendar.monthrange(selected_year, selected_month)[1]
        days_of_month = list(range(1, days_in_month + 1))

        sql = "SELECT bmi, date_recorded FROM bmi WHERE SUBSTR(date_recorded, 4, 2) = ? AND SUBSTR(date_recorded, 7, 4) = ?"
        self.cursor.execute(sql, (str(selected_month).zfill(2), str(selected_year)))
        bmi_data = self.cursor.fetchall()

        dates = []
        bmis = []

        for data in bmi_data:
            day = int(data[1].split('/')[0])
            bmi = data[0]
            dates.append(day)
            bmis.append(bmi)
        
        return [dates, bmis, days_of_month]

    def yearly_bmi_data(self, selected_year):
        months = list(range(1, 13))
        avg_bmi_values = []
        for month in months:
            sql = "SELECT bmi FROM bmi WHERE SUBSTR(date_recorded, 4, 2) = ? AND SUBSTR(date_recorded, 7, 4) = ?"
            self.cursor.execute(sql, (str(month).zfill(2), str(selected_year)))
            bmi_data = self.cursor.fetchall()

            avg_bmi = sum(bmi[0] for bmi in bmi_data) / len(bmi_data) if bmi_data else 0
            avg_bmi_values.append(avg_bmi)
        
        return [months, avg_bmi_values, calendar.month_abbr[1:]]
    
# db = LocalDB('local_db.db')
# bmi = BMI(db.connection)
# bmi.insert_bmi(76, 184, '24/02/2024')
# # bmi.remove_bmi(16)
# # print("latest bmi value:", bmi.get_most_recent_bmi())

# db.print_bmi()
# db.close_connection()