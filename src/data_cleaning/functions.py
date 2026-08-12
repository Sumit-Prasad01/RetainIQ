import matplotlib.pyplot as plt
import seaborn as sns



def categorical_sanity_check(df, column, valid_values):
    """ Function: Categories Sanity Check """

    invalid = df[~df[column].isin(valid_values)]
    return invalid[column].value_counts()



def validate_dtypes(df, expected_dtypes : dict):
    """ Function: Data Type Checking """

    mismatches = {}
    for col, dtype in expected_dtypes.items():
        if col in df.columns and df[col].dtype != dtype:
            mismatches[col] = (df[col].dtype, dtype)

    return mismatches



def missing_value_report(df):
    """ Function: Null Values Checker """

    return (
        df.isnull()
          .sum()
          .to_frame("missing_count")
          .assign(missing_pct = lambda x : x.missing_count / len(df))
          .query("missing_count > 0")
    )


# Function: Outlier Detection and Distribution

def plot_distribution(df, col):
    sns.histplot(df[col], kde = True)
    plt.title(f"Distribution of {col}")
    plt.show()


def plot_boxplot(df, col):
    sns.boxplot(x = df[col])
    plt.title(f"Outliers in {col}")
    plt.show()