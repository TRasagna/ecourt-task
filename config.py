"""
Configuration settings for eCourts Scraper
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Output directories
OUTPUT_DIR = BASE_DIR / "output"
JSON_OUTPUT_DIR = OUTPUT_DIR / "json"
PDF_OUTPUT_DIR = OUTPUT_DIR / "pdfs"
LOG_DIR = OUTPUT_DIR / "logs"

# Create directories if they don't exist
for directory in [OUTPUT_DIR, JSON_OUTPUT_DIR, PDF_OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Browser settings
HEADLESS = True  # Set to False for debugging
BROWSER_TIMEOUT = 60000  # 60 seconds
WAIT_TIMEOUT = 20000  # 20 seconds

# CAPTCHA settings
MAX_CAPTCHA_RETRIES = 5
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Will auto-detect, set manually if needed
# For Windows: r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# eCourts URLs
ECOURTS_BASE_URL = "https://services.ecourts.gov.in/ecourtindia_v6/"
ECOURTS_CAUSELIST_URL = f"{ECOURTS_BASE_URL}?p=cause_list/index"
ECOURTS_CNR_SEARCH_URL = f"{ECOURTS_BASE_URL}"

# Delhi District Courts URL
DELHI_COURTS_URL = "https://newdelhi.dcourts.gov.in/cause-list-%e2%81%84-daily-board/"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Request delays (in seconds)
REQUEST_DELAY = 2
