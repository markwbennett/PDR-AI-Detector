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

def test_case(case_number):
    """Test a single case"""
    base_url = "https://search.txcourts.gov"
    case_url = f"{base_url}/Case.aspx?cn=01-24-{case_number:05d}-CR"
    
    try:
        response = session.get(case_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for Appellant or Appellee brief
        brief_info = find_appellant_brief(soup)
        if brief_info:
            brief_link, description = brief_info
            pdf_url = urljoin(base_url, brief_link)
            filename = f"01-24-{case_number:05d}-CR {description} Brief.pdf"
            folder = "CA01_2024_Briefs"
            download_file(pdf_url, filename, folder)
            print(f"✓ Found {description} brief for case 01-24-{case_number:05d}-CR")
            return True
        else:
            print(f"✗ No appellant/appellee brief found for case 01-24-{case_number:05d}-CR")
            return False
    except Exception as e:
        print(f"✗ Error processing case 01-24-{case_number:05d}-CR: {e}")
        return False

def main():
    """Test function to try ten case numbers including 00855"""
    print("Testing First Court of Appeals scraper...")
    
    # Test cases including the specified 00855
    test_cases = [100, 200, 300, 400, 500, 600, 700, 800, 855, 900]
    
    successful_cases = []
    failed_cases = []
    
    for case_num in test_cases:
        print(f"\nTesting case {case_num:05d}...")
        success = test_case(case_num)
        
        if success:
            successful_cases.append(case_num)
        else:
            failed_cases.append(case_num)
        
        # Add a small delay between requests
        time.sleep(1.5)
    
    print(f"\n{'='*50}")
    print("TEST RESULTS")
    print(f"{'='*50}")
    print(f"Total cases tested: {len(test_cases)}")
    print(f"Cases with briefs found: {len(successful_cases)}")
    print(f"Cases without briefs: {len(failed_cases)}")
    
    if successful_cases:
        print(f"\nCases with briefs:")
        for case_num in successful_cases:
            print(f"  01-24-{case_num:05d}-CR")
    
    if failed_cases:
        print(f"\nCases without briefs:")
        for case_num in failed_cases:
            print(f"  01-24-{case_num:05d}-CR")

if __name__ == "__main__":
    main() 