from scripts.data_cleaning.functions import (categorical_sanity_check, 
                                         validate_dtypes, 
                                         missing_value_report, 
                                         plot_boxplot, 
                                         plot_distribution
                                        )

from constants import RAW_DATA_PATH, DEMOGRAPHIC_DATA_PATH, DEMOGRAPHIC_VISUALS_PATH
from utils.common_functions import load_excel

def clean_and_save_demographic_data():

    df = load_excel(RAW_DATA_PATH, sheet_name = "Demographic")

    # Categories Sanity Check
    categorical_sanity_check(df, 'Churned', [0, 1])

    # Data Type Checking
    expected_dtypes = {
        'Name': 'str',
        'Gender': 'str',
        'Age': 'int64',
        'Salary': 'float64',
        'LocationId': 'int64',
        'Churned': 'int64'
    }

    validate_dtypes(df, expected_dtypes)

    # Null Values Checker
    missing_value_report(df)

    # Outlier Detection and Distribution
    plot_distribution(
        df, 
        'Age',
        f"{DEMOGRAPHIC_VISUALS_PATH}/Distribution.png"
    )
    plot_boxplot(
        df, 
        'Age',
        f"{DEMOGRAPHIC_VISUALS_PATH}/BoxPlot.png"
    )

    # Remove Columns
    df = df.drop(['Name'], axis = 1)

    #Export File
    df.to_csv(DEMOGRAPHIC_DATA_PATH, index = False)