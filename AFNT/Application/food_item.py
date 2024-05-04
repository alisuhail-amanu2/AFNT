from datetime import datetime
import sqlite3
from local_db import LocalDB

"""
This class handles all database and other operations related to the `food_items` table from LocalDB.
"""
class FoodItem():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
    
    # Function for adding new food item record into the database
    def insert_food_item(self, food_item):
        try:
            table_name = 'food_items'
            with self.connection:
                self.cursor.execute(f"SELECT MAX(food_item_id) FROM {table_name} WHERE food_item_id LIKE 'C%'")
                latest_id = self.cursor.fetchone()[0]

            new_id_numeric = int(latest_id[1:]) + 1 if latest_id else 1
            new_id = f'C{new_id_numeric}'

            food_item['food_item_id'] = new_id

            columns = ', '.join(key for key in food_item.keys())
            placeholders = ', '.join(':' + key for key in food_item.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.connection:
                self.cursor.execute(sql, food_item)

        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting food_item: {e}")

    # Get food item records using food_item_id
    def get_food_item_by_id(self, food_item_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM food_items WHERE food_item_id=?", (food_item_id,))
            return self.cursor.fetchall()

    # Get food item record by food_item_name
    def get_food_item_by_name(self, food_item_name):
        with self.connection:
            self.cursor.execute("SELECT * FROM food_items WHERE LOWER(food_item_name) = LOWER(?)", (food_item_name,))
            return self.cursor.fetchall()

    # Updates food_item record using food_item_id and updating the values using `updated_values` dictionary 
    def update_food_item(self, food_item_id, updated_values):
        table_name = 'food_items'

        # Updating custom food items
        if food_item_id.startswith('C'):
            set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
            sql = f"UPDATE {table_name} SET {set_clause} WHERE food_item_id = :food_item_id"
            updated_values['food_item_id'] = food_item_id

            with self.connection:
                self.cursor.execute(sql, updated_values)

        # Updating preset food items, create a new custom food item
        else:
            with self.connection:
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()
                columns = [column_info[1] for column_info in columns_info]

                self.cursor.execute(f"SELECT * FROM {table_name} WHERE food_item_id = ?", (food_item_id,))
                existing_record = self.cursor.fetchone()

                if existing_record:
                    new_id_numeric = self._get_next_custom_id_numeric()
                    new_id = f'C{new_id_numeric}'

                    updated_record = dict(zip(columns, existing_record))
                    updated_record.update(updated_values)
                    updated_record['food_item_id'] = new_id

                    columns = ', '.join(key for key in updated_record.keys())
                    placeholders = ', '.join(':' + key for key in updated_record.keys())
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    self.cursor.execute(insert_sql, updated_record)

    # Handles custom food items added by user. This adds a 'C' character infront of the food_item_id to indicate that its a custom food item
    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(food_item_id, 2) AS INTEGER)) FROM food_items WHERE food_item_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    # Removes food items. Can only remove custom food items
    def remove_food_item(self, food_item_id):
        with self.connection:
            if food_item_id.startswith('C'):
                self.cursor.execute("DELETE FROM food_items WHERE food_item_id=?", (food_item_id,))
            else:
                print("Cannot delete preset food_items.")

    # Drops the food_items table from LocalDB
    def drop_food_item(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS food_items")

# connection = sqlite3.connect('local_db.db')
# food_item = FoodItem(connection)
# id = food_item.get_food_item_by_name('BUTTER,WITH SALT')

# print(id[0][0])
