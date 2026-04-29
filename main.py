import pandas as pd
from login import Login
from graph import Graph
import sys
import datetime
import os
import re

class Main:
    def __init__(self,file,employee_file):
        df = None
        self.employee_df = None
        self.logged_in = False
        self.graph = None

        #Try to read CSV files, quit if not found
        try: 
            df = pd.read_csv(file)
            self.employee_df = pd.read_csv(employee_file)
            self.graph = Graph(file)

            #Melts the DF into long format for searching
            self.df_long = (df.melt(
                id_vars=['ID','Forename','Surname','Region'],
                var_name='Date',
                value_name='Sale'
                )).assign(Date=lambda x: pd.to_datetime(x['Date'],dayfirst=True))
        except FileNotFoundError as fnf:
            print(f"Employee file not found :( \n{fnf}")
            sys.exit(1)
        
        self.login()

    #Makes sure to always quit the program when the user keyboard interrupts the program
    @staticmethod
    def safe_input(prompt:str ) -> str:
        try:
            return input(prompt)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

    #Logs the ID and time of someone attempting to log in
    @staticmethod
    def log_attempt(user_id: str):
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log_file = "login_logs.csv"
        
        # If file doesnt exist, create it with headers
        if not os.path.exists(log_file):
            pd.DataFrame(columns=["ID", "Date"]).to_csv(log_file, index=False)
        
        # Append the new log entry and write to csv
        new_entry = pd.DataFrame({"ID": [user_id], "Date": [timestamp]})
        new_entry.to_csv(log_file, mode="a", header=False, index=False)

    #Gets the user ID and password then uses Login() to check if password entered are correct then runs the menu
    def login(self):    
        tries = 3
        while tries > 0:     
            user_id = self.safe_input("Enter your id:\n").upper().strip()
            password = self.safe_input("Enter your password:\n").strip()

            self.log_attempt(user_id)

            login = Login()
            result = login.authenticate(user_id,password)
            
            if result[0]:
                print("Logged in!")
                match result[1]:
                    case 2:
                        self.logged_in = result[0]
                        self.user_menu()
                    case 1:
                        self.logged_in = result[0]
                        self.manager_menu()
            else:
                tries -= 1
                print(f"Invalid password {tries} tries left")

        if tries == 0:
            print("Out of tries lmfao")
            sys.exit()

    #Gets the start and end date from users then validates and converts to pd.Timestamp
    def get_dates(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        while True:
            try:
                date_start = self.safe_input('Please enter the beginning date(DD/MM/YYYY): ')
                date_end = self.safe_input('Please enter ending date (DD/MM/YYYY): ')        
                date_start = pd.to_datetime(date_start, format="%d/%m/%Y")
                date_end = pd.to_datetime(date_end, format="%d/%m/%Y")

                if (self.df_long["Date"] == date_start).any() and (self.df_long["Date"] == date_end).any() and (date_start < date_end):
                    return (date_start,date_end)
                else :
                    print("Dates not stored")
            except ValueError:
                print("Invalid dates")
    
    #Gets the ID of the employee the user wants to view a graph for and validates it
    def get_id(self) -> int:
        while True:
            try:
                employee_id = int(self.safe_input("Enter an ID: \n"))
                if (self.df_long["ID"] == employee_id).any():
                    return employee_id
                else:
                    print("ID doesnt exist")                
            except ValueError:
                print("Invalid ID")

    #Allows a manager to enter a password to change the passsword of a user and ensures all password requirements are met before returning
    def get_new_password(self) -> str:
        while True:                
            print("Password requirements:\n Must be atleast 10 long \n Must include upper and low case letters \n Must include a special character \n Must include a number")
            password = self.safe_input("Enter new password, can include anything")

            if (len(password) >= 10) and (re.search(r'[A-Z]', password)) and (re.search(r'[a-z]', password)) and (re.search(r'[^A-Za-z0-9]', password)) and (re.search(r'[0-9]', password)):
                return password
            else:
                print("Invalid password entered: Requirements not met")

    #Gets the user ID from the manager in order to change their passsword
    def get_user(self) -> str:
        while True:
            user_id = self.safe_input("Enter the ID of the employee e.g. EMP123: \n").upper()
            if (self.employee_df["employee_id"] == user_id).any():
                return user_id
            else:
                print("ID entered doesnt exist")

    #Displays the user menu and gets user input based on what option they chose
    def user_menu(self):
        while self.logged_in == True: 
            print("1. View Top sales people over time")
            print("2. View Average sales over time")
            print("3. View performance for a sales person over time")
            print("4. Log out")
            print("5. Quit")
            chose = 0
            while True:
                try:
                    chose = int(self.safe_input("Enter answer: \n"))
                except ValueError:
                    print("Cannot enter letters or special characters")

                if chose < 1 or chose > 5:
                    print("Only enter options from 1 to 5")
                else:
                    break
            
            match chose:
                case 1:
                    dates = self.get_dates()
                    self.graph.view_top_sales(dates[0],dates[1])
                case 2:
                    dates = self.get_dates()
                    self.graph.view_average_sales(dates[0],dates[1])
                case 3:
                    dates = self.get_dates()
                    employee_id = self.get_id()
                    self.graph.view_sales_for_employee(employee_id,dates[0],dates[1])
                case 4:
                    self.logged_in = False
                    return
                case 5:
                    print("Quiting.....")
                    sys.exit(1)
                case _:
                    #Second check incase the user gets past the first boundry check for the menu
                    print("Invalid input")

    #Displays the manager menu which has a extra option to change the password of a user and gets user input based on what option they chose
    def manager_menu(self):
        while self.logged_in == True:
            #Displays menu options
            print("1. View Top sales people over time")
            print("2. View Average sales over time")
            print("3. View performance for a sales person over time")
            print("4. To change password of a user")
            print("5. Log out")
            print("6. Quit")

            #Gets and validates the option the user chose
            chose = 0
            while True:
                try:
                    chose = int(self.safe_input("Enter answer: \n"))
                except ValueError:
                    print("Cannot enter letters or special characters")

                if chose < 1 or chose > 6:
                    print("Only enter options from 1 to 6")
                else:
                    break
            
            #Matches what the user chose to the right function
            match chose:
                case 1:
                    dates = self.get_dates()
                    self.graph.view_top_sales(dates[0],dates[1])
                case 2:
                    dates = self.get_dates()
                    self.graph.view_average_sales(dates[0],dates[1])
                case 3:
                    dates = self.get_dates()
                    employee_id = self.get_id()
                    self.graph.view_sales_for_employee(employee_id,dates[0],dates[1])
                case 4:
                    employee_id = self.get_user()

                    employee = self.employee_df.loc[self.employee_df['employee_id'] == employee_id]
                    if (employee["role"]  == "user").any():
                        new_password = self.get_new_password()
                        change_password = Login()
                        change_password.password_change(employee_id,new_password)
                    else:
                        print("Cant change password for another manager")
                case 5:
                    self.logged_in = False
                    return
                case 6:
                    print("Quiting.....")
                    sys.exit(1)
                #Second check incase the user gets past the first boundry check for the menu
                case _:
                    print("Invalid input")

if __name__ == "__main__":
    main = Main("sales_employee_data", "users_hashed.csv")