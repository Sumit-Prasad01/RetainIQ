import joblib
import pandas as pd
import psycopg2
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config.settings import settings
from constants import TESTING_DATASET_PATH, TRAINING_DATASET_PATH
from utils.logger import logger


class DatabaseManager:
    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB_NAME,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

    def fetch_data(self, query: str) -> pd.DataFrame:
        if self.connection is None:
            self.connect()
        return pd.read_sql(query, self.connection)

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class FeatureEngineer:
    @staticmethod
    def transform(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["balancesalaryratio"] = df["balance"] / df["salary"]
        df["tenurebyage"] = df["tenure"] / df["age"]
        return df


class DataPreprocessor:
    def __init__(self, target_column: str):
        self.target_column = target_column
        self.num_cols = None
        self.cat_cols = None
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    def fit(self, df: pd.DataFrame):
        X = df.drop(columns=[self.target_column])

        self.num_cols = X.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()
        self.cat_cols = X.select_dtypes(
            include=["object", "string", "bool", "category"]
        ).columns.tolist()

        self.scaler.fit(X[self.num_cols])
        if self.cat_cols:
            self.encoder.fit(X[self.cat_cols])

        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        target = df[self.target_column]
        X = df.drop(columns=[self.target_column])

        X_num = pd.DataFrame(
            self.scaler.transform(X[self.num_cols]),
            columns=self.num_cols,
            index=X.index,
        )

        if self.cat_cols:
            X_cat = pd.DataFrame(
                self.encoder.transform(X[self.cat_cols]),
                columns=self.encoder.get_feature_names_out(self.cat_cols),
                index=X.index,
            )
        else:
            X_cat = pd.DataFrame(index=X.index)

        X_processed = pd.concat([X_num, X_cat], axis=1)
        X_processed[self.target_column] = target.values

        return X_processed

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)


class DatasetPreparer:
    def __init__(
        self,
        target_column: str = "churned",
        train_fraction: float = 0.8,
        random_state: int = 200,
    ):
        self.target_column = target_column
        self.train_fraction = train_fraction
        self.random_state = random_state
        self.feature_engineer = FeatureEngineer()
        self.preprocessor = DataPreprocessor(target_column=target_column)

    def split_data(self, df: pd.DataFrame):
        df_train = df.sample(
            frac=self.train_fraction, random_state=self.random_state
        )
        df_test = df.drop(df_train.index)
        return df_train.copy(), df_test.copy()

    def prepare(self, df: pd.DataFrame):
        df_train, df_test = self.split_data(df)
        logger.info(f"Training samples: {len(df_train)}")
        logger.info(f"Testing samples: {len(df_test)}")

        df_train = self.feature_engineer.transform(df_train)
        df_test = self.feature_engineer.transform(df_test)

        df_train = self.preprocessor.fit_transform(df_train)
        df_test = self.preprocessor.transform(df_test)[df_train.columns]

        X_train = df_train.drop(columns=[self.target_column])
        y_train = df_train[self.target_column]
        X_test = df_test.drop(columns=[self.target_column])
        y_test = df_test[self.target_column]

        return X_train, y_train, X_test, y_test


class BankChurnPipeline:
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
        self.dataset_preparer = DatasetPreparer(
            target_column="churned",
            train_fraction=0.8,
            random_state=200,
        )

    def run(
        self,
        train_output_path: str = TRAINING_DATASET_PATH,
        test_output_path: str = TESTING_DATASET_PATH,
    ):
        with DatabaseManager() as db:
            df = db.fetch_data(self.QUERY)

        logger.info(f"Loaded {len(df)} records.")

        X_train, y_train, X_test, y_test = self.dataset_preparer.prepare(df)

        train_bundle = {
            "X_train": X_train,
            "y_train": y_train,
            "preprocessor": self.dataset_preparer.preprocessor,
        }

        test_bundle = {
            "X_test": X_test,
            "y_test": y_test,
            "preprocessor": self.dataset_preparer.preprocessor,
        }

        joblib.dump(train_bundle, train_output_path)
        joblib.dump(test_bundle, test_output_path)

        logger.info(f"Training dataset bundle saved to {train_output_path}")
        logger.info(f"Testing dataset bundle saved to {test_output_path}")
        logger.info(f"X_train shape: {X_train.shape}")
        logger.info(f"X_test shape: {X_test.shape}")


if __name__ == "__main__":
    BankChurnPipeline().run()