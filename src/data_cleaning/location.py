import pandas as pd

from constants import RAW_DATA_PATH, LOCATION_DATA_PATH
from utils.common_functions import load_excel


df = load_excel(RAW_DATA_PATH, sheet_name = "Location")


#Export File
df.to_csv(LOCATION_DATA_PATH, index = False)