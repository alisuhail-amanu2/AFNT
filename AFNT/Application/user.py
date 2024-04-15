import os
import csv
import re
from datetime import datetime
from datetime import datetime as dt

"""
This class handles all database and other operations related to the `users` table from CentralDB.
"""
class User:

    # Initializing centralDB csv file
    def __init__(self):
        self.current_file_path = os.path.abspath(__file__)
        self.project_root = os.path.dirname(os.path.dirname(self.current_file_path))
        self.users_file_path = os.path.join(self.project_root, 'Database', 'DatabaseCSV', 'Central', 'users.csv')

    # Remove BOM (Byte Order Mark) from the beginning of the text
    def remove_bom(self, text):
        if text.startswith('\ufeff'):
            return text[1:]
        return text

    # Gets all user data from the database
    def get_user_data(self):
        user_data = []
        with open(self.users_file_path, 'r', encoding='utf-8-sig') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                user_data.append(row)
        return user_data

    # Gets the users age using the username
    def get_user_age(self, username):
        user_data = self.get_user_data()
        for user in user_data:
            if user[1] == username:
                dob_str = user[10]
                if dob_str:
                    dob = datetime.strptime(dob_str, '%d/%m/%Y')  # parse dob string to datetime object
                    today = datetime.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    return age

    # Gets the users gender using the username
    def get_user_gender(self, username):
        user_data = self.get_user_data()
        for user in user_data:
            if user[1] == username:
                return user[9]

    # Function to verify login details and allow user to login. Returns 0 for successful login, else 1 for invalid username and 2 for invalid password
    def handle_login(self, login_details):
        user_data = self.get_user_data()

        for user in user_data:
            if login_details[0] == user[1]:
                if login_details[1] == user[2]:
                    return 0  # Successful login
                else:
                    return 2  # Invalid Password

        return 1  # Invalid Username

    # Handles validation for user registration
    def handle_registration(self, reg_details):
        user_data = self.get_user_data()

        if len(reg_details[0]) > 10:
            return 3  # Username too Long

        if any(reg_details[0] == user[1] for user in user_data):
            return 4  # User Already Exists

        if not self.is_valid_email(reg_details[1]):
            return 5  # Invalid Email

        if any(reg_details[1] == user[4] for user in user_data):
            return 6  # Email Used by Another User

        if len(reg_details[2]) < 3:
            return 7  # Password too Short

        if not self.is_valid_phone(reg_details[3]):
            return 8  # Invalid Phone Number

        if not self.is_valid_age(reg_details[4]):
            return 9  # Invalid Age

        # Append the new user to the CSV file
        with open(self.users_file_path, 'a', newline='') as csvfile:
            fieldnames = ['user_id', 'username', 'password', 'type', 'email', 'county_code', 'phone',
                        'address', 'postcode_zipcode', 'gender', 'dob', 'date_enrolled', 'time_enrolled', 'is_active']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Get the next available user_id
            user_id = len(user_data)

            # Write the new user data to the CSV file
            writer.writerow({
                'user_id': user_id,
                'username': reg_details[0],
                'password': reg_details[2],
                'type': 'User',
                'email': reg_details[1],
                'county_code': 0,
                'phone': reg_details[3],
                'address': '',
                'postcode_zipcode': '',
                'gender': reg_details[5],
                'dob': reg_details[4],
                'date_enrolled': dt.now().strftime('%d/%m/%Y'),
                'time_enrolled': dt.now().strftime('%H:%M:%S'),
                'is_active': 1,
            })
        return 10

    # Validate email format
    def is_valid_email(self, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email)

    # Validate phone number format
    def is_valid_phone(self, phone):
        phone_regex = r'^\d{10,}$'
        return re.match(phone_regex, phone)

    # Validate user's age. User must be 13+ to use the app
    def is_valid_age(self, dob):
        dob_date = dt.strptime(dob, "%Y-%m-%d").date()
        today = datetime.today().date()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        return age >= 13
