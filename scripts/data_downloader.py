import requests
from pathlib import Path

from config.settings import settings
from utils.logger import logger
from utils.custom_exception import CustomException
from constants import RAW_DATA_PATH

def download_google_sheet(sheet_id: str, output_path: str):

    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.info("Data downloaded successfully.")
        logger.info(f"Downloaded: {output_path}")

    except Exception as e:
        logger.error(f"Failed to download data : {e}")
        raise CustomException("Error while downloading data : ", e)


if __name__ == "__main__":
    SHEET_ID = settings.SHEET_ID

    OUTPUT_PATH = RAW_DATA_PATH 

    download_google_sheet(SHEET_ID, OUTPUT_PATH)