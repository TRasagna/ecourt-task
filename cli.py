#!/usr/bin/env python3
"""
Command Line Interface for eCourts Scraper
"""
import argparse
import sys
from src.scraper import eCourtsScraper
from src.utils import get_today_date, get_tomorrow_date
import json

def main():
    parser = argparse.ArgumentParser(
        description='eCourts Scraper - Download court case information and cause lists',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by CNR
  python cli.py --cnr KARC010037582023

  # Check if case is listed today
  python cli.py --cnr KARC010037582023 --today

  # Check if case is listed tomorrow
  python cli.py --cnr KARC010037582023 --tomorrow

  # Download cause list for today
  python cli.py --causelist --state "Karnataka" --district "Bangalore" --court-complex "City Civil Court"

  # Download cause list for specific date
  python cli.py --causelist --state "Delhi" --district "Central" --court-complex "Patiala House" --date "21-10-2025"
        """
    )

    # CNR search options
    parser.add_argument('--cnr', type=str, help='CNR number to search')
    parser.add_argument('--today', action='store_true', help='Check if case is listed today')
    parser.add_argument('--tomorrow', action='store_true', help='Check if case is listed tomorrow')

    # Cause list options
    parser.add_argument('--causelist', action='store_true', help='Download cause list')
    parser.add_argument('--causelist-all', action='store_true', help='Download cause lists for all courts in complex')
    parser.add_argument('--state', type=str, help='State name')
    parser.add_argument('--district', type=str, help='District name')
    parser.add_argument('--court-complex', type=str, help='Court complex name')
    parser.add_argument('--court-name', type=str, help='Specific court name (optional)')
    parser.add_argument('--date', type=str, help='Date for cause list (DD-MM-YYYY format, default: today)')
    parser.add_argument('--type', type=str, choices=['Civil', 'Criminal'], default='Civil', 
                       help='Type of cause list (Civil/Criminal)')

    # General options
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--output', type=str, help='Custom output file path')

    args = parser.parse_args()

    # Validate arguments
    if not any([args.cnr, args.causelist, args.causelist_all]):
        parser.print_help()
        sys.exit(1)

    # Initialize scraper
    print("Initializing eCourts Scraper...")
    scraper = eCourtsScraper(headless=args.headless)

    try:
        # CNR search
        if args.cnr:
            if args.today:
                print(f"\nChecking if case {args.cnr} is listed today...")
                result = scraper.check_case_today(args.cnr)
            elif args.tomorrow:
                print(f"\nChecking if case {args.cnr} is listed tomorrow...")
                result = scraper.check_case_tomorrow(args.cnr)
            else:
                print(f"\nSearching for case: {args.cnr}")
                result = scraper.search_by_cnr(args.cnr)

            if result:
                print("\n" + "="*50)
                print("RESULTS:")
                print("="*50)
                print(json.dumps(result, indent=2))
                print("="*50)
            else:
                print("\nNo results found or error occurred.")

        # Cause list download
        elif args.causelist or args.causelist_all:
            if not all([args.state, args.district, args.court_complex]):
                print("Error: --state, --district, and --court-complex are required for cause list download")
                sys.exit(1)

            date = args.date if args.date else get_today_date()

            print(f"\nDownloading cause list:")
            print(f"  State: {args.state}")
            print(f"  District: {args.district}")
            print(f"  Court Complex: {args.court_complex}")
            print(f"  Date: {date}")
            print(f"  Type: {args.type}")

            result = scraper.download_cause_list(
                state=args.state,
                district=args.district,
                court_complex=args.court_complex,
                court_name=args.court_name,
                date=date,
                list_type=args.type
            )

            if result:
                print(f"\n✓ Cause list saved to: {result}")
            else:
                print("\n✗ Failed to download cause list")

    finally:
        print("\nClosing scraper...")
        scraper.close()
        print("Done!")

if __name__ == '__main__':
    main()
