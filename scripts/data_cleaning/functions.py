import matplotlib.pyplot as plt
import seaborn as sns

from utils.logger import logger


def categorical_sanity_check(df, column, valid_values):
    """ Function: Categories Sanity Check """

    invalid = df[~df[column].isin(valid_values)]
    total_invalids =  invalid[column].value_counts()

    logger.info(f"Total number of invalid values : {total_invalids}")



def validate_dtypes(df, expected_dtypes : dict):
    """ Function: Data Type Checking """

    mismatches = {}
    for col, dtype in expected_dtypes.items():
        if col in df.columns and df[col].dtype != dtype:
            mismatches[col] = (df[col].dtype, dtype)

    logger.info(f"Mistatches : {mismatches}")



def missing_value_report(df):
    """ Function: Null Values Checker """

    null_values =  (
        df.isnull()
          .sum()
          .to_frame("missing_count")
          .assign(missing_pct = lambda x : x.missing_count / len(df))
          .query("missing_count > 0")
    )

    logger.info(f"Total null values : {null_values}")


# Function: Outlier Detection and Distribution

def plot_distribution(df, col, visuals_path):
    sns.histplot(df[col], kde = True)
    plt.title(f"Distribution of {col}")
    plt.savefig(visuals_path)
    plt.show()


def plot_boxplot(df, col, visuals_path):
    sns.boxplot(x = df[col])
    plt.title(f"Outliers in {col}")
    plt.savefig(visuals_path)
    plt.show()