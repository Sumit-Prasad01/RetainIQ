from pathlib import Path

#RAW DATA PATH
RAW_DATA_DIR = Path("artifacts/raw_data")
RAW_DATA_PATH = RAW_DATA_DIR / "banking_customer_data.xlsx"

#PROCESSED DATA PATH
PROCESSED_DATA_DIR = Path("artifacts/processed_data")

ACCOUNTS_DATA_PATH = PROCESSED_DATA_DIR / "accounts.csv"
DEMOGRAPHIC_DATA_PATH = PROCESSED_DATA_DIR / "demographic.csv"
LOCATION_DATA_PATH = PROCESSED_DATA_DIR / "location.csv"