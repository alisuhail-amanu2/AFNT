from datetime import datetime
import sqlite3
from local_db import LocalDB

class FoodItemLog():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def insert_food_item_log(self, food_item_log):
        try:
            with self.connection:
                columns = ', '.join(food_item_log.keys())
                values = [food_item_log.get(key, '') for key in food_item_log.keys()]
                placeholders = ', '.join('?' for _ in food_item_log.values())

                sql = f"""
                    INSERT INTO food_item_logs 
                    ({columns}) 
                    VALUES ({placeholders})
                """
                self.cursor.execute(sql, values)

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                print("Error: Invalid food_item_id or workout_log_id.")
            else:
                print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting food_item log: {e}")

    def get_food_item_log_by_id(self, food_item_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM food_item_logs WHERE food_item_log_id=?", (food_item_log_id,))
            return self.cursor.fetchall()

    def update_food_item_log(self, food_item_log_id, updated_values):
        table_name = 'food_item_logs'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE food_item_log_id = :food_item_log_id"
        updated_values['food_item_log_id'] = food_item_log_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(food_item_log_id, 2) AS INTEGER)) FROM food_item_logs WHERE food_item_log_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    def remove_food_item_log(self, food_item_log_id):
        with self.connection:
            self.cursor.execute("DELETE FROM food_item_logs WHERE food_item_log_id=?", (food_item_log_id,))

    def drop_food_item_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS food_item_logs")