import csv

"""
This class is used for generating and synching body data gathered by the Arduino Watch to the AFNT App and the LocalDB (Incomplete).
Also gets the body data collected by the Arduino Watch from the csv file called `arduino.csv`. The following data is obtained from the csv file:
Heart rate (BPM), blood oxygen level (%), step count and body temperature (°C).
"""
class ArduinoWatch():

    # Returns heart rate and the epoch time in a list ['heart_rate', 'epoch_time']
    def heart_rate_data(self):
        heart_rate_list = []
        try:
            with open(r'F:\arduino.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
            
                for row in reader:
                    heart_rate = int(row['heart_rate'])
                    epoch_time = row['epoch_time']
                    heart_rate_list.append((epoch_time, heart_rate))

        except FileNotFoundError:
            print("File not found!")
        except Exception as e:
            print("Error:", e)
        return heart_rate_list
    
    # Returns blood oxygen level and the epoch time in a list ['oxygen_level', 'epoch_time']
    def oxygen_level_data(self):
        oxygen_level_list = []
        try:
            with open(r'F:\arduino.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
            
                for row in reader:
                    oxygen_level = int(row['oxygen_level'])
                    epoch_time = row['epoch_time']
                    oxygen_level_list.append((epoch_time, oxygen_level))
                    
        except FileNotFoundError:
            print("File not found!")
        except Exception as e:
            print("Error:", e)
        
        return oxygen_level_list

    # Returns body temperature and the epoch time in a list ['temperature_celsius', 'epoch_time']
    def body_temperature_data(self):
        body_temperature_list = []
        try:
            with open(r'F:\arduino.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
            
                for row in reader:
                    body_temperature = int(row['temperature_celsius'])
                    epoch_time = row['epoch_time']
                    body_temperature_list.append((epoch_time, body_temperature))
                    
        except FileNotFoundError:
            print("File not found!")
        except Exception as e:
            print("Error:", e)
        
        return body_temperature_list

    # Returns step count and the epoch time in a list ['step_count', 'epoch_time']
    def step_count_data(self):
        step_count_list = []
        try:
            with open(r'F:\arduino.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
            
                for row in reader:
                    step_count = int(row['step_count'])
                    epoch_time = row['epoch_time']
                    step_goal_percent = row['step_goal_percent']
                    step_count_list.append((epoch_time, step_count, step_goal_percent))
                    
        except FileNotFoundError:
            print("File not found!")
        except Exception as e:
            print("Error:", e)
        
        return step_count_list