import pandas as pd
import matplotlib.pyplot as plt
import sys

class Graph:
    def __init__(self,file):
        #Try to read the csv file for sales employees, quit if not found
        df = None
        try: 
            df = pd.read_csv(file)
        except FileNotFoundError as fnf:
            print(f"Employee file not found :( \n{fnf}")
            sys.exit(1)

        #Melts the DF into long format for searching and plotting
        self.df_long = None
        self.df_long = (df.melt(
            id_vars=['ID','Forename','Surname','Region'],
            var_name='Date',
            value_name='Sale'
            )).assign(Date=lambda x: pd.to_datetime(x['Date'],dayfirst=True))
    
    #Filters the Dataframe given for inbetween the start and end date
    @staticmethod
    def search_dates(df,date_start,date_end):
        df_searched = df.loc[
            (df["Date"]>=date_start) &
            (df["Date"]<=date_end)
        ]
        return df_searched

    def view_top_sales(self,date_start,date_end):
        df_searched = self.search_dates(self.df_long, date_start, date_end)
        df_values = df_searched.groupby("ID")["Sale"].sum().reset_index()
        df_values_descending = df_values.sort_values('Sale',ascending=False)

        df_values_descending.set_index("ID")["Sale"].plot(kind='bar')
        plt.ylabel("Total sales made")
        plt.xlabel("Employee ID")
        plt.xticks(rotation=45)
        plt.title(f"Total Sales overtime for employees inbetween {date_start} and {date_end}")
        
        start_str = date_start.strftime('%d-%m-%Y')
        end_str = date_end.strftime('%d-%m-%Y')
        plt.savefig(f'Sales_inbetween_{start_str}_{end_str}')
        plt.show()
    
    def view_average_sales(self,date_start,date_end):
        df_searched = self.search_dates(self.df_long, date_start, date_end)
        df_values = df_searched.groupby("ID")["Sale"].mean().reset_index()
        df_values_descending = df_values.sort_values('Sale',ascending=False)

        df_values_descending.set_index("ID")["Sale"].plot(kind='barh')
        plt.xlabel("Average sale made")
        plt.ylabel("Employee ID")
        plt.title(f"Average sales for each employee inbetween {date_start} and {date_end}")
        
        start_str = date_start.strftime('%d-%m-%Y')
        end_str = date_end.strftime('%d-%m-%Y')
        plt.savefig(f'Average_sales_inbetween_{start_str}_{end_str}')
        plt.show()

    def view_sales_for_employee(self, employee_id, date_start, date_end):
        df_searched = self.search_dates(self.df_long, date_start, date_end)
        df_values = df_searched.loc[df_searched["ID"] == employee_id]
        date_labels = df_values["Date"].dt.strftime('%d/%m/%Y')

        plt.plot(date_labels, df_values["Sale"])
        plt.ylabel("Sale amount")
        plt.xlabel("Date")
        plt.xticks(rotation=45)
        plt.title(f"Sales over time for {employee_id} inbetween {date_start} and {date_end}")
        
        start_str = date_start.strftime('%d-%m-%Y')
        end_str = date_end.strftime('%d-%m-%Y')
        plt.savefig(f'Sales_for_{employee_id}_inbetween_{start_str}_{end_str}')
        plt.show()