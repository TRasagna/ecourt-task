# eCourts Scraper

A comprehensive Python application to scrape court listings and cause lists from eCourts India Services.

## Features

- ✅ Search cases by CNR number or Case details
- ✅ Check if case is listed today or tomorrow
- ✅ Download cause lists for any date
- ✅ Automatic CAPTCHA solving using Tesseract OCR
- ✅ Download case PDFs
- ✅ CLI interface with multiple options
- ✅ Simple web interface
- ✅ Export results as JSON
- ✅ Robust error handling and logging

## Installation

### Prerequisites

1. Python 3.8 or higher
2. Tesseract OCR installed on your system

#### Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### Install Python Dependencies

```bash
# Clone or extract the project
cd ecourts_scraper

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Usage

### Command Line Interface (CLI)

#### 1. Search Case by CNR

```bash
python cli.py --cnr KARC010037582023
```

#### 2. Check if case is listed today

```bash
python cli.py --cnr KARC010037582023 --today
```

#### 3. Check if case is listed tomorrow

```bash
python cli.py --cnr KARC010037582023 --tomorrow
```

#### 4. Download cause list for today

```bash
python cli.py --causelist --state "Karnataka" --district "Bangalore" --court-complex "City Civil Court"
```

#### 5. Download cause list for specific date

```bash
python cli.py --causelist --state "Karnataka" --district "Bangalore" --court-complex "City Civil Court" --date "21-10-2025"
```

#### 6. Download cause list for all courts in a complex

```bash
python cli.py --causelist-all --state "Karnataka" --district "Bangalore" --court-complex "City Civil Court"
```

### Web Interface

```bash
python web_ui/app.py
```

Then open your browser and navigate to: `http://localhost:5000`

### Python API

```python
from src.scraper import eCourtsScraper

# Initialize scraper
scraper = eCourtsScraper()

# Search by CNR
case_info = scraper.search_by_cnr("KARC010037582023")
print(case_info)

# Download cause list
scraper.download_cause_list(
    state="Karnataka",
    district="Bangalore",
    court_complex="City Civil Court",
    date="21-10-2025"
)

# Close scraper
scraper.close()
```

## Output

All outputs are saved in the `output/` directory:

- **JSON files**: `output/json/`
- **PDF files**: `output/pdfs/`
- **Logs**: `output/logs/`

## Configuration

Edit `config.py` to customize:

- Browser settings (headless mode, timeout)
- Tesseract path
- Output directories
- Retry attempts for CAPTCHA

## Troubleshooting

### CAPTCHA solving fails

- Ensure Tesseract is properly installed and in PATH
- Adjust CAPTCHA preprocessing in `src/captcha_solver.py`
- Increase retry attempts in `config.py`

### Browser issues

- Ensure Playwright browsers are installed: `playwright install chromium`
- Try running in non-headless mode for debugging (set `HEADLESS=False` in config)

### Website structure changes

- The scraper may need updates if eCourts website structure changes
- Check logs in `output/logs/` for detailed error information

## Project Structure

```
ecourts_scraper/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── cli.py             # Command-line interface
├── config.py          # Configuration settings
├── src/               # Core scraper modules
├── web_ui/            # Web interface
├── output/            # Output directory
└── tests/             # Unit tests
```

## Legal Disclaimer

This tool is for educational and research purposes only. Users must:

- Comply with eCourts Terms of Service
- Not overload the servers with excessive requests
- Use responsibly and ethically
- Respect data privacy and copyright

## Author

Developed as an internship task submission.

## License

MIT License - See LICENSE file for details
