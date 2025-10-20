"""
Unit tests for eCourts Scraper
"""
import unittest
from src.scraper import eCourtsScraper
from src.captcha_solver import CaptchaSolver
from src.utils import setup_logger, format_date

class TestCaptchaSolver(unittest.TestCase):
    def setUp(self):
        self.solver = CaptchaSolver()

    def test_solver_initialization(self):
        self.assertIsNotNone(self.solver)

class TestUtils(unittest.TestCase):
    def test_format_date(self):
        result = format_date("20-10-2025")
        self.assertEqual(result, "20-10-2025")

    def test_logger_setup(self):
        logger = setup_logger("test")
        self.assertIsNotNone(logger)

class TestScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = eCourtsScraper(headless=True)

    def tearDown(self):
        self.scraper.close()

    def test_scraper_initialization(self):
        self.assertIsNotNone(self.scraper)
        self.assertIsNotNone(self.scraper.page)

if __name__ == '__main__':
    unittest.main()
