from src.data_processing import BankChurnPreprocessor
from src.model_training import ModelTraining

from constants import *

if __name__ == "__main__":

    BankChurnPreprocessor().run()
    trainer = ModelTraining(
            data_path=TRAIN_DATA_PATH,
            model_output_path=MODEL_OUTPUT_PATH,
        )
    trainer.run()