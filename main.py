#!/usr/bin/env python3
"""
Main entry point for eCourts Scraper
"""
from src.scraper import eCourtsScraper
from src.utils import get_today_date

def main():
    """Example usage of the scraper"""
    print("eCourts Scraper - Example Usage")
    print("=" * 50)

    # Example 1: Search by CNR
    print("\nExample 1: Searching by CNR...")
    with eCourtsScraper() as scraper:
        result = scraper.search_by_cnr("KARC010037582023")
        if result:
            print("Case found!")
            print(result)
        else:
            print("Case not found or error occurred")

    # Example 2: Download cause list
    print("\nExample 2: Downloading cause list...")
    with eCourtsScraper() as scraper:
        result = scraper.download_cause_list(
            state="Karnataka",
            district="Bangalore",
            court_complex="City Civil Court",
            date=get_today_date()
        )
        if result:
            print(f"Cause list downloaded: {result}")
        else:
            print("Failed to download cause list")

    print("\n" + "=" * 50)
    print("Examples completed!")

if __name__ == '__main__':
    main()
