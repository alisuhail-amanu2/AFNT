from datetime import datetime
import sqlite3
from local_db import LocalDB
import matplotlib.pyplot as plt

class Height():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_height(self, height, selected_date):
        try:
            current_time = datetime.now().strftime('%H:%M:%S')

            with self.connection:
                self.cursor.execute("SELECT * FROM height WHERE date_recorded = ?", (selected_date,))
                existing_height = self.cursor.fetchone()

                if existing_height:
                    sql = """
                        UPDATE height 
                        SET height_m = ?, time_recorded = ?
                        WHERE date_recorded = ?
                    """
                    self.cursor.execute(sql, (height, current_time, selected_date))
                else:
                    sql = """
                        INSERT INTO height (height_m, date_recorded, time_recorded)
                        VALUES (?, ?, ?)
                    """
                    self.cursor.execute(sql, (height, selected_date, current_time))

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid workout_id or height_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting height data: {e}")

    def get_height_by_id(self, height_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM height WHERE height_id=?", (height_id,))
            return self.cursor.fetchall()
        
    def get_latest_height_value(self):
        try:
            with self.connection:
                # Retrieve the latest height value
                self.cursor.execute("SELECT height_m FROM height ORDER BY SUBSTR(date_recorded, 7, 4) || '-' || SUBSTR(date_recorded, 4, 2) || '-' || SUBSTR(date_recorded, 1, 2) DESC LIMIT 1")
                latest_height = self.cursor.fetchone()
                return latest_height[0] if latest_height else None
        except Exception as e:
            print(f"Error retrieving latest height value: {e}")
            return None


        except sqlite3.Error as e:
            print(f"Error retrieving latest height value: {e}")

    def update_height(self, height_id, updated_values):
        table_name = 'height'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE height_id = :height_id"
        updated_values['height_id'] = height_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    def remove_height(self, height_id):
        with self.connection:
            self.cursor.execute("DELETE FROM height WHERE height_id=?", (height_id,))

    def drop_height(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS height")
    
    def verify_height(self, height):
        if not height:
            return 24  # empty height
        try:
            # Convert height data from string to float
            height_float = int(height)
            return 22  # valid height
        except ValueError:
            return 23  # invalid height format

# db = LocalDB('local_db.db')
# height = Height(db.connection)

# height.insert_height(189, '29/02/2024')
# print(height.verify_height(['232.3', '04/02/2024']))
# db.print_height()
# print("latest height value", height.get_latest_height_value())

# db.close_connection()