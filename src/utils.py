"""
Utility functions for eCourts Scraper
"""
import json
import logging
from pathlib import Path
from datetime import datetime
import config

def setup_logger(name: str) -> logging.Logger:
    """Setup logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler
    log_file = config.LOG_DIR / f"ecourts_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def save_json(data: dict, filename: str, output_dir: Path = config.JSON_OUTPUT_DIR) -> Path:
    """Save data as JSON file"""
    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath

def save_pdf(pdf_content: bytes, filename: str, output_dir: Path = config.PDF_OUTPUT_DIR) -> Path:
    """Save PDF content to file"""
    filepath = output_dir / filename
    with open(filepath, 'wb') as f:
        f.write(pdf_content)
    return filepath

def format_date(date_str: str, input_format: str = "%d-%m-%Y", output_format: str = "%d-%m-%Y") -> str:
    """Format date string"""
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except:
        return date_str

def get_today_date(format: str = "%d-%m-%Y") -> str:
    """Get today's date in specified format"""
    return datetime.now().strftime(format)

def get_tomorrow_date(format: str = "%d-%m-%Y") -> str:
    """Get tomorrow's date in specified format"""
    from datetime import timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    return tomorrow.strftime(format)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
