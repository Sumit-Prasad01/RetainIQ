import pandas as pd
import psycopg2

from pathlib import Path

from constants import (
                        ACCOUNTS_DATA_CSV_PATH, 
                        DEMOGRAPHIC_DATA_CSV_PATH, 
                        LOCATION_DATA_CSV_PATH, 
                        CREATE_TABLES_PATH
                    )
from utils.logger import logger
from utils.custom_exception import CustomException
from utils.common_functions import load_csv
from config.settings import settings


# LOAD DATA
location_df = load_csv(LOCATION_DATA_CSV_PATH)
demographic_df = load_csv(DEMOGRAPHIC_DATA_CSV_PATH)
account_df = load_csv(ACCOUNTS_DATA_CSV_PATH)

logger.info(f"Loaded {len(location_df)} location records")
logger.info(f"Loaded {len(demographic_df)} demographic records")
logger.info(f"Loaded {len(account_df)} account records")


# CREATE POSTGRESQL CONNECTION
conn = psycopg2.connect(
    host = settings.POSTGRES_HOST,
    port = settings.POSTGRES_PORT,
    database = settings.POSTGRES_DB_NAME,
    user = settings.POSTGRES_USER,
    password = settings.POSTGRES_PASSWORD
)

cursor = conn.cursor()


try:

    # CREATE TABLES
    
    logger.info("Creating database tables...")

    with open(CREATE_TABLES_PATH, "r", encoding="utf-8") as sql_file:
        create_tables_sql = sql_file.read()

    cursor.execute(create_tables_sql)

    logger.info("Tables checked/created successfully")

    # INSERT LOCATION DATA

    logger.info("Inserting location data...")

    for _, row in location_df.iterrows():

        cursor.execute(
            """
            INSERT INTO location (
                LocationId,
                Geography
            )
            VALUES (%s, %s)
            ON CONFLICT (LocationId) DO NOTHING
            """,
            (
                int(row["LocationId"]),
                row["Geography"]
            )
        )

    logger.info(
        f"Location data inserted successfully "
        f"({len(location_df)} records)"
    )

    # INSERT DEMOGRAPHIC DATA

    logger.info("Inserting demographic data...")

    for _, row in demographic_df.iterrows():

        cursor.execute(
            """
            INSERT INTO demographic (
                CustomerId,
                Gender,
                Age,
                Salary,
                LocationId,
                Churned
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (CustomerId) DO NOTHING
            """,
            (
                int(row["CustomerId"]),
                row["Gender"],
                int(row["Age"]),
                float(row["Salary"]),
                int(row["LocationId"]),
                bool(row["Churned"])
            )
        )

    logger.info(
        f"Demographic data inserted successfully "
        f"({len(demographic_df)} records)"
    )

    # INSERT ACCOUNT DATA

    logger.info("Inserting account data...")

    for _, row in account_df.iterrows():

        cursor.execute(
            """
            INSERT INTO account (
                CustomerId,
                Tenure,
                Balance,
                NumProducts,
                HasCreditCard,
                IsActive
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (CustomerId) DO NOTHING
            """,
            (
                int(row["CustomerId"]),
                int(row["Tenure"]),
                float(row["Balance"]),
                int(row["NumProducts"]),
                bool(row["HasCreditCard"]),
                bool(row["IsActive"])
            )
        )

    logger.info(
        f"Account data inserted successfully "
        f"({len(account_df)} records)"
    )


    # COMMIT ALL CHANGES

    conn.commit()

    logger.info("\nAll data inserted successfully!")


except Exception as e:

    # ROLLBACK

    conn.rollback()

    logger.error(f"Error during data ingestion: {e}")
    raise CustomException("Failed to ingest data to db : ", e)


finally:

    # CLOSE CONNECTION

    cursor.close()
    conn.close()

    logger.info("PostgreSQL connection closed.")