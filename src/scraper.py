"""
Main scraper module for eCourts
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from typing import Optional, Dict, List
import time
from datetime import datetime, timedelta
import json
import config
from .captcha_solver import CaptchaSolver
from .utils import setup_logger, save_json, save_pdf, get_today_date, get_tomorrow_date, sanitize_filename
from .models import CaseInfo, CauseList, CauseListEntry
from bs4 import BeautifulSoup

class eCourtsScraper:
    """Main scraper class for eCourts India Services"""

    def __init__(self, headless: bool = config.HEADLESS):
        self.logger = setup_logger(__name__)
        self.captcha_solver = CaptchaSolver()
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        self._initialize_browser()

    def _initialize_browser(self):
        """Initialize Playwright browser"""
        try:
            self.logger.info("Initializing browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = self.context.new_page()
            self.page.set_default_timeout(config.BROWSER_TIMEOUT)
            self.logger.info("Browser initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing browser: {e}")
            raise

    def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _solve_captcha_with_retry(self, max_retries: int = config.MAX_CAPTCHA_RETRIES) -> bool:
        """Solve CAPTCHA with retry mechanism"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"CAPTCHA solving attempt {attempt + 1}/{max_retries}")

                # Wait for CAPTCHA image to load
                captcha_img = self.page.wait_for_selector("img[id*='captcha' i], img[src*='captcha' i]", timeout=5000)

                if not captcha_img:
                    self.logger.warning("CAPTCHA image not found")
                    continue

                # Get CAPTCHA image
                captcha_bytes = captcha_img.screenshot()

                # Solve CAPTCHA
                captcha_text = self.captcha_solver.solve_captcha(captcha_bytes)

                if not captcha_text:
                    # Try numeric solver
                    captcha_text = self.captcha_solver.solve_numeric_captcha(captcha_bytes)

                if captcha_text:
                    # Find and fill CAPTCHA input
                    captcha_input = self.page.query_selector("input[placeholder='Enter Captcha']")
                    if captcha_input:
                        captcha_input.fill(captcha_text)
                        self.logger.info(f"CAPTCHA filled: {captcha_text}")
                        return True

                # Refresh CAPTCHA if available
                refresh_btn = self.page.query_selector("a[onclick*='captcha' i], button[onclick*='captcha' i]")
                if refresh_btn:
                    refresh_btn.click()
                    time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error in CAPTCHA solving attempt {attempt + 1}: {e}")
                time.sleep(1)

        self.logger.error("Failed to solve CAPTCHA after all retries")
        return False

    def search_by_cnr(self, cnr: str) -> Optional[Dict]:
        """Search case by CNR number"""
        try:
            self.logger.info(f"Searching case with CNR: {cnr}")

            # Navigate to CNR search page
            self.page.goto(config.ECOURTS_CNR_SEARCH_URL)
            
            # Click on the CNR Number button in the search menu
            try:
                self.page.click("text=CNR Number", timeout=config.WAIT_TIMEOUT)
            except PlaywrightTimeout:
                self.logger.error("'CNR Number' button not found. Taking a screenshot.")
                self.page.screenshot(path="cnr_button_not_found.png")
                return None

            # Wait for the page to load and check for the CNR input field
            try:
                cnr_input = self.page.wait_for_selector("#cino", timeout=config.WAIT_TIMEOUT)
                cnr_input.fill(cnr)
            except PlaywrightTimeout:
                self.logger.error("CNR input field not found. Taking a screenshot.")
                self.page.screenshot(path="cnr_input_not_found.png")
                return None

            # Solve CAPTCHA
            if not self._solve_captcha_with_retry():
                return None

            # Click search
            search_btn = self.page.query_selector("button:has-text('Search')")
            if search_btn:
                search_btn.click()
                self.page.wait_for_load_state('networkidle')
            else:
                self.logger.error("Search button not found.")
                self.page.screenshot(path="search_button_not_found.png")
                return None

            # Extract case information
            case_info = self._extract_case_info(cnr)

            if case_info:
                # Save to JSON
                filename = f"case_{sanitize_filename(cnr)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                save_json(case_info, filename)
                self.logger.info(f"Case info saved to {filename}")

            return case_info

        except Exception as e:
            self.logger.error(f"Error searching by CNR: {e}")
            self.page.screenshot(path="error_searching_by_cnr.png")
            return None

    def _extract_case_info(self, cnr: str) -> Optional[Dict]:
        """Extract case information from the page"""
        try:
            html = self.page.content()
            soup = BeautifulSoup(html, 'lxml')
            case_info = CaseInfo(cnr=cnr)

            # Case Details Table
            details_table = soup.find('table', class_='case_details_table')
            if details_table:
                rows = details_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        label = cells[0].get_text(strip=True)
                        if 'Case Type' in label:
                            case_info.case_type = cells[1].get_text(strip=True)
                        elif 'Filing Number' in label:
                            # Filing number is in the same row as filing date
                            case_info.filing_date = cells[3].get_text(strip=True)
                        elif 'Registration Number' in label:
                            case_info.case_number = cells[1].get_text(strip=True)
                            # Registration date is in the same row
                            case_info.registration_date = cells[3].get_text(strip=True)

            # Case Status Table
            status_table = soup.find('table', class_='case_status_table')
            if status_table:
                rows = status_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if 'Next Hearing Date' in label:
                            case_info.next_hearing = value
                        elif 'Case Stage' in label:
                            case_info.status = value
                        elif 'Court Number and Judge' in label:
                            case_info.court_name = value

            # Petitioner and Advocate Table
            petitioner_table = soup.find('table', class_='Petitioner_Advocate_table')
            if petitioner_table:
                case_info.petitioner = petitioner_table.get_text(strip=True)

            # Respondent and Advocate Table
            respondent_table = soup.find('table', class_='Respondent_Advocate_table')
            if respondent_table:
                case_info.respondent = respondent_table.get_text(strip=True)

            return case_info.to_dict()

        except Exception as e:
            self.logger.error(f"Error extracting case info: {e}")
            return None

    def check_case_listed(self, cnr: str, date: str) -> Optional[Dict]:
        """Check if case is listed on specific date"""
        try:
            self.logger.info(f"Checking if case {cnr} is listed on {date}")

            # First get case info
            case_info = self.search_by_cnr(cnr)

            if not case_info:
                return None

            # Check if next hearing matches the date
            next_hearing = case_info.get('next_hearing', '')

            result = {
                'cnr': cnr,
                'date_checked': date,
                'is_listed': date in next_hearing if next_hearing else False,
                'case_info': case_info
            }

            return result

        except Exception as e:
            self.logger.error(f"Error checking case listing: {e}")
            return None

    def check_case_today(self, cnr: str) -> Optional[Dict]:
        """Check if case is listed today"""
        today = get_today_date()
        return self.check_case_listed(cnr, today)

    def check_case_tomorrow(self, cnr: str) -> Optional[Dict]:
        """Check if case is listed tomorrow"""
        tomorrow = get_tomorrow_date()
        return self.check_case_listed(cnr, tomorrow)

    def download_cause_list(self, state: str, district: str, court_complex: str, 
                           court_name: Optional[str] = None, date: Optional[str] = None, 
                           list_type: str = "Civil") -> Optional[str]:
        """Download cause list for specified parameters"""
        try:
            if not date:
                date = get_today_date()

            self.logger.info(f"Downloading cause list for {state}/{district}/{court_complex} on {date}")

            # Navigate to cause list page
            self.page.goto(config.ECOURTS_CAUSELIST_URL)
            time.sleep(2)

            # Select state
            state_select = self.page.wait_for_selector("select[name*='state' i], select[id*='state' i]", timeout=10000)
            if state_select:
                state_select.select_option(label=state)
                time.sleep(1)

            # Select district
            district_select = self.page.wait_for_selector("select[name*='district' i], select[id*='district' i]", timeout=10000)
            if district_select:
                district_select.select_option(label=district)
                time.sleep(1)

            # Select court complex
            complex_select = self.page.wait_for_selector("select[name*='complex' i], select[id*='complex' i]", timeout=10000)
            if complex_select:
                complex_select.select_option(label=court_complex)
                time.sleep(1)

            # Select court name if provided
            if court_name:
                court_select = self.page.wait_for_selector("select[name*='court' i], select[id*='court_name' i]", timeout=10000)
                if court_select:
                    court_select.select_option(label=court_name)
                    time.sleep(1)
            else:
                # Select first available court
                court_select = self.page.wait_for_selector("select[name*='court' i], select[id*='court_name' i]", timeout=10000)
                if court_select:
                    options = court_select.query_selector_all("option")
                    if len(options) > 1:
                        options[1].click()
                        time.sleep(1)

            # Fill date
            date_input = self.page.query_selector("input[type='text'][name*='date' i], input[id*='date' i]")
            if date_input:
                date_input.fill(date)

            # Solve CAPTCHA
            if not self._solve_captcha_with_retry():
                self.logger.error("Failed to solve CAPTCHA")
                return None

            # Click appropriate button (Civil/Criminal)
            if list_type.lower() == "civil":
                submit_btn = self.page.query_selector("input[value*='Civil' i], button:has-text('Civil')")
            else:
                submit_btn = self.page.query_selector("input[value*='Criminal' i], button:has-text('Criminal')")

            if submit_btn:
                # Setup download handler
                with self.page.expect_download() as download_info:
                    submit_btn.click()
                    time.sleep(3)

                # Check if download occurred
                try:
                    download = download_info.value
                    filename = f"causelist_{sanitize_filename(state)}_{sanitize_filename(district)}_{date.replace('-', '')}_{list_type}.pdf"
                    filepath = config.PDF_OUTPUT_DIR / filename
                    download.save_as(filepath)
                    self.logger.info(f"Cause list downloaded: {filepath}")
                    return str(filepath)
                except:
                    # If no download, try to extract from page
                    self.logger.info("No PDF download, attempting to extract from page")
                    cause_list_data = self._extract_cause_list_from_page(state, district, court_complex, date, list_type)

                    if cause_list_data:
                        filename = f"causelist_{sanitize_filename(state)}_{sanitize_filename(district)}_{date.replace('-', '')}_{list_type}.json"
                        filepath = save_json(cause_list_data, filename)
                        self.logger.info(f"Cause list data saved: {filepath}")
                        return str(filepath)

            return None

        except Exception as e:
            self.logger.error(f"Error downloading cause list: {e}")
            return None

    def _extract_cause_list_from_page(self, state: str, district: str, court_complex: str, 
                                      date: str, list_type: str) -> Optional[Dict]:
        """Extract cause list data from HTML page"""
        try:
            # Wait for table to load
            table = self.page.wait_for_selector("table", timeout=10000)

            if not table:
                return None

            entries = []
            rows = self.page.query_selector_all("table tr")

            for row in rows[1:]:  # Skip header
                cells = row.query_selector_all("td")
                if len(cells) >= 3:
                    entry = CauseListEntry(
                        serial_number=cells[0].inner_text().strip(),
                        case_number=cells[1].inner_text().strip(),
                        petitioner=cells[2].inner_text().strip() if len(cells) > 2 else None,
                        respondent=cells[3].inner_text().strip() if len(cells) > 3 else None,
                        advocate=cells[4].inner_text().strip() if len(cells) > 4 else None
                    )
                    entries.append(entry)

            cause_list = CauseList(
                date=date,
                state=state,
                district=district,
                court_complex=court_complex,
                court_name="",
                list_type=list_type,
                entries=entries
            )

            return cause_list.to_dict()

        except Exception as e:
            self.logger.error(f"Error extracting cause list from page: {e}")
            return None
