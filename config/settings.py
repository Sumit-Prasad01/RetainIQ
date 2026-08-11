import os 

from dotenv import load_dotenv

load_dotenv()


class Settings:

    SHEET_ID = os.getenv("SHEET_ID")


settings = Settings()
