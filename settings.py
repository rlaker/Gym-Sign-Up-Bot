import os
from dotenv import load_dotenv

load_dotenv(override=True)

DRIVER_PATH = os.getenv('TENNIS_DRIVER_PATH')
USERNAME = os.getenv('TENNIS_USERNAME')
PASSWORD = os.getenv('TENNIS_PASSWORD')
URL = os.getenv('TENNIS_URL')

