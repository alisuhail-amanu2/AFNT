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

    def get_food_item_logs_details(self, meal_log_id):
        try:
            with self.connection:
                self.cursor.execute("""
                    SELECT 
                        fil.food_item_log_id,
                        fi.food_item_name,
                        fil.serving,
                        ROUND(fi.energy_kcal * fil.serving) AS total_energy_kcal,
                        ROUND(fi.protein_g * fil.serving, 1) AS total_protein_g,
                        ROUND(fi.lipid_g * fil.serving, 1) AS total_lipid_g,
                        ROUND(fi.carbs_g * fil.serving, 1) AS total_carbs_g,
                        ROUND(fi.sugar_g * fil.serving, 1) AS total_sugar_g,
                        ROUND(fi.fiber_td_g * fil.serving, 1) AS total_fiber_td_g,
                        ROUND(fi.iron_mg * fil.serving, 1) AS total_iron_mg,
                        CASE 
                            WHEN fil.ate = 1 THEN 'Yes' 
                            ELSE 'No' 
                        END AS ate
                    FROM 
                        food_item_logs AS fil
                    JOIN 
                        food_items AS fi ON fil.food_item_id = fi.food_item_id
                    WHERE 
                        fil.meal_log_id = ? AND
                        fil.is_active = 1;
                """, (meal_log_id,))
                return self.cursor.fetchall()

        except Exception as e:
            print(f"Error retrieving exercise logs details: {e}")
            return []

    # Update food_item_log record using food_item_log_id and updating the values using `updated_values` dictionary 
    def update_food_item_log(self, food_item_log_id, updated_values):
        table_name = 'food_item_logs'
        set_clause = ', '.join(f"{key} = :{key}" for key in updated_values.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE food_item_log_id = :food_item_log_id"
        updated_values['food_item_log_id'] = food_item_log_id

        with self.connection:
            self.cursor.execute(sql, updated_values)

    # Function for removing the food item log by setting `is_active` field to `0`. The database will only display those records with is_active = 1
    def remove_food_item_log(self, food_item_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE food_item_logs SET is_active = 0 WHERE food_item_log_id=?", (food_item_log_id,))
        except Exception as e:
            print(f"Error removing food_item log: {e}")

    # Function to readd the removed food_item log by setting its is_active to 1.
    def re_add_food_item_log(self, food_item_log_id):
        try:
            with self.connection:
                self.cursor.execute("UPDATE food_item_logs SET is_active = 1 WHERE food_item_log_id=?", (food_item_log_id,))
        except Exception as e:
            print(f"Error removing food_item log: {e}")

    # Drops the food_item_logs table from LocalDB
    def drop_food_item_log(self):
        with self.connection:
            self.cursor.execute("DROP TABLE IF EXISTS food_item_logs")

# connection = sqlite3.connect('local_db.db')
# food_item_log = FoodItemLog(connection)

# food_item_log.re_add_food_item_log(5)

# print(food_item_log.get_food_item_logs_details('3'))