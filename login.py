import pandas as pd
import bcrypt
import sys

class Login:
    def __init__(self):
        #Try to read the csv file for employees, quit if not found
        self.df = None
        try: 
            self.df = pd.read_csv("users_hashed.csv")
        except FileNotFoundError as fnf:
            print(f"Employee file not found :( \n{fnf}")
            sys.exit(1)

    #Checks if the password is correct for the employee ID selected
    def authenticate(self, id, password):
        #Searches for the row of the employee selected and returns False if not found
        employee_row = self.df.loc[self.df["employee_id"] == id]
        if employee_row.empty:
            print("Employee not found.")
            return False, None

        #Get the stored hash from the employee csv file
        stored_hash = employee_row["password"].iloc[0]
        #Checks if the entered password matches the stored hash
        is_match = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        #Deletes the stored hash from the program for security
        del stored_hash

        #Returns 1/2 based if the employee is a user or manager
        if is_match:
            role = employee_row["role"].iloc[0]
            match role:
                case "user":
                    access_level = 2
                case "manager":
                    access_level = 1
                case _:
                    print(f"Unknown role: {role}")
                    return False, None
            return True, access_level
        else:
            print("Invalid password.")
            return False, None

    #Hashes passwords and returns them for changing passwords
    @staticmethod
    def hash_password(plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    
    #Changes the password of a employee
    def password_change(self,user,new_password):
        #Hashes and deletes the plain text password
        hashed_password = self.hash_password(new_password)
        del new_password

        #Changes the password of the employee
        self.df.loc[self.df["employee_id"] == user, "password"] = hashed_password

        #Makes the changes to the CSV file
        self.df.to_csv("users_hashed.csv", index=False)
