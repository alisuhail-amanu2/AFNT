from flask import Flask, render_template, request
import os

app = Flask(__name__)

script_dir = os.path.dirname(os.path.abspath(__file__))
users_file_path = os.path.join(script_dir, 'Database', 'DatabaseCSV', 'Central', 'users.csv')

# Function to check login information
def check_login(username, password):
    with open(users_file_path, mode='r', encoding='utf-8') as csv_file:
        for line in csv_file:
            data = line.strip().split(',')
            if len(data) >= 3 and data[1] == username and data[2] == password:
                return True
    return False

@app.route('/', methods=['GET', 'POST'])
def login():
    error_message = None 

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check login information
        if check_login(username, password):
            print(f"Logged in: {username}")
            return render_template('2_main.html')
        else:
            print("Login failed")
            error_message = 'Invalid Credentials'

    return render_template('1_login.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)