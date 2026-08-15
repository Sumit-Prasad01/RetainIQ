from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

from utils.logger import logger
from config.settings import settings
from constants import (
    CHURNRATE_GENDER_QUERY_PATH,
    DIFFERENCE_AVERAGE_CHURNRATE_QUERY_PATH,
    DYNAMIC_PARAMETERS_QUERY_PATH,
)


# ============================================================
# SQL QUERY FILES
# ============================================================
# Each entry is a (path, params) tuple.
# params is either None (no placeholders in the SQL file) or a
# dict matching the %(name)s placeholders used in that file.

QUERY_FILES = [
    (CHURNRATE_GENDER_QUERY_PATH, None),
    (DIFFERENCE_AVERAGE_CHURNRATE_QUERY_PATH, None),
    (
        DYNAMIC_PARAMETERS_QUERY_PATH,
        {
            "min_tenure": 9,
            "max_balance": 120000,
            "max_product": 6,
        },
    ),
]


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    logger.info("Connecting to PostgreSQL...")

    connection = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB_NAME,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    )

    logger.info("PostgreSQL connection successful.")

    return connection


# ============================================================
# READ SQL FILE
# ============================================================

def read_sql_file(sql_path):

    sql_path = Path(sql_path)

    logger.info(
        "Reading SQL file: %s",
        sql_path
    )

    if not sql_path.exists():

        raise FileNotFoundError(
            f"SQL file not found: {sql_path}"
        )

    sql = sql_path.read_text(
        encoding="utf-8"
    ).strip()

    if not sql:

        raise ValueError(
            f"SQL file is empty: {sql_path}"
        )

    return sql


# ============================================================
# EXECUTE QUERY
# ============================================================

def execute_query(connection, sql_path, params=None):

    sql_path = Path(sql_path)

    logger.info("=" * 80)
    logger.info(
        "Executing query: %s",
        sql_path.name
    )
    logger.info("=" * 80)

    try:

        # ----------------------------------------------------
        # Read SQL
        # ----------------------------------------------------

        sql = read_sql_file(sql_path)

        logger.info(
            "SQL Query:\n%s",
            sql
        )

        if params:

            logger.info(
                "Parameters: %s",
                params
            )

        # ----------------------------------------------------
        # Execute SQL
        # ----------------------------------------------------

        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(sql, params)

            # ------------------------------------------------
            # Query returned rows
            # ------------------------------------------------

            if cursor.description:

                results = cursor.fetchall()

                logger.info(
                    "Rows returned: %d",
                    len(results)
                )

                if results:

                    logger.info("Query Results:")

                    for index, row in enumerate(
                        results,
                        start=1
                    ):

                        logger.info(
                            "Row %d: %s",
                            index,
                            dict(row)
                        )

                else:

                    logger.info(
                        "Query returned no rows."
                    )

            # ------------------------------------------------
            # INSERT / UPDATE / DELETE
            # ------------------------------------------------

            else:

                logger.info(
                    "Rows affected: %d",
                    cursor.rowcount
                )

        connection.commit()

        logger.info(
            "SUCCESS: %s",
            sql_path.name
        )

    except Exception as e:

        connection.rollback()

        logger.exception(
            "FAILED: %s",
            sql_path.name
        )

        logger.error(
            "Error: %s",
            str(e)
        )


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("=" * 80)
    logger.info("EDA QUERY EXECUTION STARTED")
    logger.info("=" * 80)

    connection = None

    try:

        # --------------------------------------------------------
        # Display configured SQL files
        # --------------------------------------------------------

        logger.info(
            "Number of EDA queries: %d",
            len(QUERY_FILES)
        )

        for query_path, _ in QUERY_FILES:

            logger.info(
                "Query file: %s",
                query_path
            )

        # --------------------------------------------------------
        # Connect to PostgreSQL
        # --------------------------------------------------------

        connection = get_connection()

        # --------------------------------------------------------
        # Execute all queries
        # --------------------------------------------------------

        for query_path, params in QUERY_FILES:

            execute_query(
                connection,
                query_path,
                params
            )

    except psycopg2.Error as e:

        logger.exception(
            "PostgreSQL error: %s",
            str(e)
        )

    except Exception as e:

        logger.exception(
            "EDA execution failed: %s",
            str(e)
        )

    finally:

        if connection:

            connection.close()

            logger.info(
                "PostgreSQL connection closed."
            )

    logger.info("=" * 80)
    logger.info("EDA QUERY EXECUTION COMPLETED")
    logger.info("=" * 80)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()