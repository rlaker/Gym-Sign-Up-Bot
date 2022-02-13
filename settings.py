import os

from dotenv import load_dotenv

load_dotenv(override=True)

DRIVER_PATH = os.getenv("TENNIS_DRIVER_PATH")
USERNAME = os.getenv("TENNIS_USERNAME")
PASSWORD = os.getenv("TENNIS_PASSWORD")
URL = os.getenv("TENNIS_URL")
TENNIS_EMAIL_SENDER = os.getenv("TENNIS_EMAIL_SENDER")
TENNIS_TEST_EMAIL = os.getenv("TENNIS_TEST_EMAIL")
