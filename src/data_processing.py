import joblib
import pandas as pd
import psycopg2

from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config.settings import settings
from constants import TESTING_DATASET_PATH, TRAINING_DATASET_PATH
from utils.logger import logger


class BankChurnPreprocessor:

    QUERY = """
        SELECT
            d.gender,
            d.age,
            d.salary,
            l.geography,
            a.tenure,
            a.balance,
            a.numproducts,
            a.hascreditcard,
            a.isactive,
            d.churned
        FROM demographic d
        JOIN account a
            ON a.customerid = d.customerid
        JOIN location l
            ON l.locationid = d.locationid
    """

    def __init__(self):
        self.scaler = StandardScaler()

        self.encoder = OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False
        )

    def run(self):

        # Load data from PostgreSQL
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB_NAME,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

        try:
            df = pd.read_sql(self.QUERY, conn)
        finally:
            conn.close()

        logger.info(f"Loaded {len(df)} records.")

        # Train / Test Split
        df_train = df.sample(
            frac=0.8,
            random_state=200
        )

        df_test = df.drop(df_train.index).copy()
        df_train = df_train.copy()

        logger.info(
            f"Training samples: {len(df_train)}"
        )

        logger.info(
            f"Testing samples: {len(df_test)}"
        )

        # Feature Engineering
        for data in [df_train, df_test]:

            data["balancesalaryratio"] = (
                data["balance"]
                / data["salary"].replace(0, 1)
            )

            data["tenurebyage"] = (
                data["tenure"]
                / data["age"].replace(0, 1)
            )

        # =============================================
        # Separate Features / Target
        # =============================================

        X_train = df_train.drop(
            columns=["churned"]
        )

        y_train = df_train["churned"]

        X_test = df_test.drop(
            columns=["churned"]
        )

        y_test = df_test["churned"]

        # =============================================
        # Identify Numerical / Categorical Columns
        # =============================================

        num_cols = X_train.select_dtypes(
            include="number"
        ).columns

        cat_cols = X_train.select_dtypes(
            include=["object", "string", "bool", "category"]
        ).columns

        # =============================================
        # Numerical Features
        # =============================================

        X_train_num = pd.DataFrame(
            self.scaler.fit_transform(
                X_train[num_cols]
            ),
            columns=num_cols,
            index=X_train.index
        )

        X_test_num = pd.DataFrame(
            self.scaler.transform(
                X_test[num_cols]
            ),
            columns=num_cols,
            index=X_test.index
        )

        # =============================================
        # Categorical Features
        # =============================================

        X_train_cat = pd.DataFrame(
            self.encoder.fit_transform(
                X_train[cat_cols]
            ),
            columns=self.encoder.get_feature_names_out(
                cat_cols
            ),
            index=X_train.index
        )

        X_test_cat = pd.DataFrame(
            self.encoder.transform(
                X_test[cat_cols]
            ),
            columns=self.encoder.get_feature_names_out(
                cat_cols
            ),
            index=X_test.index
        )

        # =============================================
        # Combine Features
        # =============================================

        X_train = pd.concat(
            [X_train_num, X_train_cat],
            axis=1
        )

        X_test = pd.concat(
            [X_test_num, X_test_cat],
            axis=1
        )

        # =============================================
        # Save Dataset Bundle
        # =============================================

        artifacts = {
            "X_train": X_train,
            "y_train": y_train,
            "X_test": X_test,
            "y_test": y_test
        }

        joblib.dump(
            artifacts,
            TRAINING_DATASET_PATH
        )

        logger.info(
            f"Dataset bundle saved to: "
            f"{TRAINING_DATASET_PATH}"
        )

        logger.info(
            f"X_train shape: {X_train.shape}"
        )

        logger.info(
            f"X_test shape: {X_test.shape}"
        )


if __name__ == "__main__":
    BankChurnPreprocessor().run()