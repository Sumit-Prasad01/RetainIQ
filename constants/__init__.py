from pathlib import Path
import os 

#VISUALS
VISUALS_PATH = Path("artifacts/visuals")

ACCOUNTS_VISUALS_PATH = VISUALS_PATH / "accounts_visuals"
ACCOUNTS_VISUALS_PATH.mkdir(parents=True, exist_ok=True)

DEMOGRAPHIC_VISUALS_PATH = VISUALS_PATH / "demographic_visuals"
DEMOGRAPHIC_VISUALS_PATH.mkdir(parents=True, exist_ok=True)

# SQL PATH
CREATE_TABLES_PATH = "sql/data_ingestion/create_tables.sql"

#RAW DATA PATH
RAW_DATA_DIR = Path("artifacts/raw_data")
RAW_DATA_PATH = RAW_DATA_DIR / "banking_customer_data.xlsx"

#PROCESSED DATA PATH
PROCESSED_DATA_DIR = Path("artifacts/processed_data")

ACCOUNTS_DATA_PATH = PROCESSED_DATA_DIR / "accounts.csv"
DEMOGRAPHIC_DATA_PATH = PROCESSED_DATA_DIR / "demographic.csv"
LOCATION_DATA_PATH = PROCESSED_DATA_DIR / "location.csv"

ACCOUNTS_DATA_CSV_PATH = "artifacts/processed_data/accounts.csv"           
DEMOGRAPHIC_DATA_CSV_PATH = "artifacts/processed_data/demographic.csv"           
LOCATION_DATA_CSV_PATH = "artifacts/processed_data/location.csv"           

#EDA 
EDA_QUERIES_PATH = Path("sql/eda_queries")
CHURNRATE_GENDER_QUERY_PATH = EDA_QUERIES_PATH / "churnRate_across_genders.sql"
DIFFERENCE_AVERAGE_CHURNRATE_QUERY_PATH = EDA_QUERIES_PATH / "difference_average_churnRate.sql"
DYNAMIC_PARAMETERS_QUERY_PATH = EDA_QUERIES_PATH / "dynamic_parameters.sql"

# TRAIN TEST
PROCESSED_DATA_DIR = "artifacts/processed_data"
TRAINING_DATASET_PATH = os.path.join(PROCESSED_DATA_DIR, "train_bundle.pkl")

TRAIN_DATA_PATH = os.path.join("artifacts/processed_data/train_bundle.pkl")

MODEL_OUTPUT_PATH = "artifacts/models/lgbm_model.pkl"