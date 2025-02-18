import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_URL = os.getenv('BASE_URL')
    REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')
    TIMEOUT = int(os.getenv('TIMEOUT', 10))
