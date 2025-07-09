#!/./.venv/bin/python

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import main as scraper_main

def main():
    print("PDR AI Detector - Texas Courts Scraper")
    print("=====================================")
    print()
    
    choice = input("Choose an option:\n1. Run full scraper (PD-0001-24 to PD-1081-24)\n2. Test scraper on sample cases\n3. Run AI detection on downloaded PDRs\n4. Exit\n\nEnter choice (1-4): ")
    
    if choice == "1":
        confirm = input("\nThis will scrape 1081 cases and may take a while. Continue? (y/N): ")
        if confirm.lower() == 'y':
            scraper_main()
        else:
            print("Cancelled.")
    elif choice == "2":
        print("\nRunning test scraper...")
        os.system("./.venv/bin/python test_scraper.py")
    elif choice == "3":
        print("\nRunning AI detection on PDR documents...")
        os.system("./.venv/bin/python ai_detector.py")
    elif choice == "4":
        print("Goodbye!")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main() 