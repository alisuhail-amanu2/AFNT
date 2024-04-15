from datetime import datetime
import sqlite3
from local_db import LocalDB

"""
This class handles all database and other operations related to the `food_item_logs` table from LocalDB.
"""
class FoodItemLog():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    # Function for adding new food item log record into the database
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

    # Get food item log records using food_item_log_id
    def get_food_item_log_by_id(self, food_item_log_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM food_item_logs WHERE food_item_log_id=?", (food_item_log_id,))
            return self.cursor.fetchall()

    # Update food_item_log record using food_item_log_id and updating the values using `updated_values` dictionary 
    def update_food_item_log(self, food_item_log_id, updated_values):
        table_name = 'food_item_logs'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE food_item_log_id = :food_item_log_id"
        updated_values['food_item_log_id'] = food_item_log_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    # Function for removing food_item_log using food_item_log_id
    def remove_food_item_log(self, food_item_log_id):
        with self.connection:
            self.cursor.execute("DELETE FROM food_item_logs WHERE food_item_log_id=?", (food_item_log_id,))

    # Drops the food_item_logs table from LocalDB
    def drop_food_item_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS food_item_logs")