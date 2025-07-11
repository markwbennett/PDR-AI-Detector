#!/./.venv/bin/python

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
import random

# Create a session with browser-like headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
})

def download_file(url, filename, folder):
    """Download a file from URL and save it locally"""
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Create folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)
        
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def find_appellant_brief(soup):
    """Find Appellant brief in Appellate Briefs table"""
    # Find the Appellate Briefs section - look for div containing "Appellate Briefs" text
    briefs_div = soup.find('div', class_=['panel-heading', 'panel-heading-content'], string=lambda text: text and 'Appellate Briefs' in text.strip())
    if not briefs_div:
        return None
    
    # Find the table with briefs - look for RadGrid table
    panel = briefs_div.parent
    table = panel.find('table', class_='rgMasterTable')
    if not table:
        return None
    
    # Look through table rows
    rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 4:
            # Check columns: Date, Event Type, Description, Document
            event_type = cells[1].get_text().strip()
            description = cells[2].get_text().strip()
            
            # Look for event type containing "Brief filed" by "Appellant" or "Appellee" (but not State)
            if "Brief filed" in event_type and (description == "Appellant" or description == "Appellee") and description != "State":
                # Check the document cell (4th column)
                doc_cell = cells[3]
                
                # Look for nested document table
                doc_table = doc_cell.find('table', class_='docGrid')
                if doc_table:
                    doc_rows = doc_table.find_all('tr')
                    for doc_row in doc_rows:
                        doc_cells = doc_row.find_all('td')
                        if len(doc_cells) >= 2:
                            # Check if this row contains Brief (not Notice)
                            doc_type = doc_cells[1].get_text().strip()
                            if 'Brief' in doc_type and 'Notice' not in doc_type:
                                # Get the link from the first cell
                                link = doc_cells[0].find('a')
                                if link and link.get('href'):
                                    return (link['href'], description)
    
    return None

def scrape_case_with_backoff(court_num, case_number, max_retries=3):
    """Scrape a single case with exponential backoff on errors"""
    for attempt in range(max_retries):
        try:
            return scrape_case(court_num, case_number)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                backoff_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Request failed for case {court_num:02d}-24-{case_number:05d}-CR (attempt {attempt + 1}), backing off for {backoff_time:.1f} seconds: {e}")
                time.sleep(backoff_time)
            else:
                print(f"Max retries exceeded for case {court_num:02d}-24-{case_number:05d}-CR: {e}")
                return False
        except Exception as e:
            print(f"Unexpected error for case {court_num:02d}-24-{case_number:05d}-CR: {e}")
            return False
    
    return False

def scrape_case(court_num, case_number):
    """Scrape a single case page for appellant brief"""
    base_url = "https://search.txcourts.gov"
    case_url = f"{base_url}/Case.aspx?cn={court_num:02d}-24-{case_number:05d}-CR"
    
    response = session.get(case_url, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check if Appellate Briefs section exists
    briefs_div = soup.find('div', class_=['panel-heading', 'panel-heading-content'], string=lambda text: text and 'Appellate Briefs' in text.strip())
    if not briefs_div:
        print(f"No Appellate Briefs section for case {court_num:02d}-24-{case_number:05d}-CR")
        return "no_briefs"
    
    # Look for Appellant or Appellee brief
    brief_info = find_appellant_brief(soup)
    if brief_info:
        brief_link, description = brief_info
        pdf_url = urljoin(base_url, brief_link)
        filename = f"{court_num:02d}-24-{case_number:05d}-CR {description} Brief.pdf"
        folder = f"CA{court_num:02d}_2024_Briefs"
        download_file(pdf_url, filename, folder)
        print(f"Found {description} brief for case {court_num:02d}-24-{case_number:05d}-CR")
        return True
    else:
        print(f"No appellant/appellee brief found for case {court_num:02d}-24-{case_number:05d}-CR")
        return True

def scrape_court(court_num, start_case=1, end_case=None):
    """Scrape all cases for a specific court"""
    print(f"Starting scraper for Court of Appeals {court_num:02d}...")
    if end_case:
        print(f"Processing cases {court_num:02d}-24-{start_case:05d}-CR through {court_num:02d}-24-{end_case:05d}-CR")
    else:
        print(f"Processing cases starting from {court_num:02d}-24-{start_case:05d}-CR (no end limit)")
    
    failed_cases = []
    consecutive_no_briefs = 0
    case_num = start_case
    
    while True:
        if end_case and case_num > end_case:
            break
        result = scrape_case_with_backoff(court_num, case_num)
        if result == False:
            failed_cases.append(case_num)
        elif result == "no_briefs":
            consecutive_no_briefs += 1
            if consecutive_no_briefs >= 50:
                print(f"Stopping: 50 consecutive cases without Appellate Briefs section (last case: {court_num:02d}-24-{case_num:05d}-CR)")
                break
        else:
            consecutive_no_briefs = 0
        
        # Add a small delay to be respectful to the server
        base_delay = 1.0
        jitter = random.uniform(0, 0.5)
        time.sleep(base_delay + jitter)
        
        # Progress indicator
        if case_num % 100 == 0:
            if end_case:
                print(f"Progress: {case_num}/{end_case} cases processed for Court {court_num:02d}")
            else:
                print(f"Progress: {case_num} cases processed for Court {court_num:02d}")
        
        case_num += 1
    
    print(f"Scraping completed for Court {court_num:02d}!")
    
    if failed_cases:
        print(f"\nFailed to process {len(failed_cases)} cases:")
        for case_num in failed_cases:
            print(f"  {court_num:02d}-24-{case_num:05d}-CR")

def main():
    """Main function to scrape both courts"""
    print("Starting Courts of Appeals document scraper...")
    
    # Scrape First Court of Appeals starting from case 516
    scrape_court(1, 516)
    
    # Scrape Fourteenth Court of Appeals starting from case 12
    scrape_court(14, 12)

if __name__ == "__main__":
    main() 