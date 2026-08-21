import subprocess
import threading
import time
from dotenv import load_dotenv

from utils.logger import get_logger
from utils.custom_exception import CustomException

logger = get_logger(__name__)

load_dotenv()


def run_backend():
    try:
        logger.info("Starting backend service.")

        subprocess.run(
            [
                "uvicorn",
                "backend.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            check=True,
        )

    except subprocess.CalledProcessError as e:
        logger.error("Problem with backend service.")
        raise CustomException("Failed to start backend", e)
    

def run_frontend():
    try:

        logger.info("Starting frontend service")
        subprocess.run(["streamlit", "run", "frontend/app.py"], check = True)
    
    except CustomException as e:
        logger.error("Problem with frontend service")
        raise CustomException("Failed to start frontend", e)
    


if __name__ == "__main__":
    try:

        threading.Thread(target = run_backend).start()
        time.sleep(2)
        run_frontend()

    except CustomException as e:
        logger.exception(f"Custom Exception occured : {str(e)}")