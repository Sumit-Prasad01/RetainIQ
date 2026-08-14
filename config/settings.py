import os 

from dotenv import load_dotenv

load_dotenv()


class Settings:

    SHEET_ID = os.getenv("SHEET_ID")

    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
    POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


settings = Settings()
