import os
from dotenv import load_dotenv

load_dotenv(override=True)

DRIVER_PATH = os.getenv('DRIVER_PATH')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
ERNIE_URL = os.getenv('ERNIE_URL')

