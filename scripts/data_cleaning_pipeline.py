from scripts.data_cleaning.account import clean_and_save_accounts_data
from scripts.data_cleaning.demographic import clean_and_save_demographic_data
from scripts.data_cleaning.location import clean_and_save_location_data

def clean_data():
    clean_and_save_accounts_data()
    clean_and_save_demographic_data()
    clean_and_save_location_data()


    
if __name__ == "__main__":

    clean_data()