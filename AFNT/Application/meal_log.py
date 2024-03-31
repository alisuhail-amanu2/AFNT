from datetime import datetime
import sqlite3
from local_db import LocalDB

class MealLog():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

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

    def get_meal_log_by_id(self, meal_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM meal_logs WHERE meal_log_id=?", (meal_log_id,))
            return self.cursor.fetchall()

    def update_meal_log(self, meal_log_id, updated_values):
        table_name = 'meal_logs'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE meal_log_id = :meal_log_id"
        updated_values['meal_log_id'] = meal_log_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(meal_log_id, 2) AS INTEGER)) FROM meal_logs WHERE meal_log_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    def remove_meal_log(self, meal_log_id):
        with self.connection:
            self.cursor.execute("DELETE FROM meal_logs WHERE meal_log_id=?", (meal_log_id,))

    def drop_meal_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS meal_logs")