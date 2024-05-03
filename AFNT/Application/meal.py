from datetime import datetime
import sqlite3
from local_db import LocalDB

"""
This class handles all database and other operations related to the `meals` table from LocalDB.
"""
class Meal():

    # Initializing LocalDB connection
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    # Function for adding new meal record into the database
    def insert_meal(self, meal):
        try:
            table_name = 'meals'
            with self.connection:
                self.cursor.execute(f"SELECT MAX(meal_id) FROM {table_name} WHERE meal_id LIKE 'C%'")
                latest_id = self.cursor.fetchone()[0]

            new_id_numeric = int(latest_id[1:]) + 1 if latest_id else 1
            new_id = f'C{new_id_numeric}'

            meal['meal_id'] = new_id

            columns = ', '.join(key for key in meal.keys())
            placeholders = ', '.join(':' + key for key in meal.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.connection:
                self.cursor.execute(sql, meal)

        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")

        except Exception as e:
            print(f"Error inserting meal: {e}")

    # Gets meal record by meal_id
    def get_meal_by_id(self, meal_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM meals WHERE meal_id=?", (meal_id,))
            return self.cursor.fetchall()

    # Gets meal record by type
    def get_meal_by_type(self, type):
        with self.connection:
            self.cursor.execute("SELECT * FROM meals WHERE LOWER(type) = LOWER(?)", (type,))
            return self.cursor.fetchall()

    def get_meal_details(self):
        try:

            with self.connection:
                # Use parameterized query to prevent SQL injection
                query = """
                    SELECT 
                        meal_id,
                        type,
                        description
                    FROM 
                        meals
                    WHERE 
                        is_active = 1
                """

                self.cursor.execute(query)
                meals = self.cursor.fetchall()
                
                return meals

        except Exception as e:
            print(f"Error retrieving meal logs: {e}")
            return []

    # Update meal record using meal_id and updating the values using `updated_values` dictionary 
    def update_meal(self, meal_id, updated_values):
        table_name = 'meals'

        # For custom meals
        if meal_id.startswith('C'):
            set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
            sql = f"UPDATE {table_name} SET {set_clause} WHERE meal_id = :meal_id"
            updated_values['meal_id'] = meal_id

            with self.connection:
                self.cursor.execute(sql, updated_values)

        # For preset meals, create a new custom meal record
        else:
            with self.connection:
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()
                columns = [column_info[1] for column_info in columns_info]

                self.cursor.execute(f"SELECT * FROM {table_name} WHERE meal_id = ?", (meal_id,))
                existing_record = self.cursor.fetchone()

                if existing_record:
                    new_id_numeric = self._get_next_custom_id_numeric()
                    new_id = f'C{new_id_numeric}'

                    updated_record = dict(zip(columns, existing_record))
                    updated_record.update(updated_values)
                    updated_record['meal_id'] = new_id

                    columns = ', '.join(key for key in updated_record.keys())
                    placeholders = ', '.join(':' + key for key in updated_record.keys())
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    self.cursor.execute(insert_sql, updated_record)

    # Handles custom meals added by user. This adds a 'C' character infront of the meal_id to indicate that its a custom meal
    def _get_next_custom_id_numeric(self):
        with self.connection:
            self.cursor.execute("SELECT MAX(CAST(SUBSTR(meal_id, 2) AS INTEGER)) FROM meals WHERE meal_id LIKE 'C%'")
            latest_id_numeric = self.cursor.fetchone()[0]

        return latest_id_numeric + 1 if latest_id_numeric else 1

    # Function for removing the meal by setting `is_active` field to `0`. The database will only display those records with is_active = 1
    def remove_meal(self, meal_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE meals SET is_active = 0 WHERE meal_id=?", (meal_id,))
        except Exception as e:
            print(f"Error removing meal: {e}")

    # Function to readd the removed meal by setting its is_active to 1.
    def re_add_meal(self, meal_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE meals SET is_active = 1 WHERE meal_id=?", (meal_id,))
        except Exception as e:
            print(f"Error removing meal: {e}")

    # Drops meals table from LocalDB
    def drop_meal(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS meals")

# connection = sqlite3.connect('local_db.db')
# meal = Meal(connection)


# print(meal.get_meal_details())