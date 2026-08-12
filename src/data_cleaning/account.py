import pandas as pd

from src.data_cleaning.functions import (categorical_sanity_check, 
                                         validate_dtypes, 
                                         missing_value_report, 
                                         plot_boxplot, 
                                         plot_distribution
                                        )

from constants import RAW_DATA_PATH, ACCOUNTS_DATA_PATH
from utils.common_functions import load_excel

df = load_excel(RAW_DATA_PATH, sheet_name = "Account")


# Categories Sanity Check
categorical_sanity_check(df, 'IsActive', [0, 1])


# Data Type Checking
expected_dtypes = {
    'Tenure': 'int64',
    'Balance': 'float64',
    'NumProducts': 'int64',
    'HasCreditCard': 'int64',
    'IsActive': 'int64'
}

validate_dtypes(df, expected_dtypes)


# Null Values Checker
missing_value_report(df)


# Outlier Detection and Distribution
plot_distribution(df, 'Balance')
plot_boxplot(df, 'NumProducts')


# Dealing with missing values
df['Balance'] = df['Balance'].fillna(df['Balance'].mean(), inplace = True)


# Remove Columns
df = df.drop(['AccountId'], axis = 1)

#Export File
df.to_csv(ACCOUNTS_DATA_PATH, index = False)