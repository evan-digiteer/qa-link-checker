import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_URL = os.getenv('BASE_URL')
    REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')
    TIMEOUT = int(os.getenv('TIMEOUT', 30))  # Increased default timeout
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', 30))
