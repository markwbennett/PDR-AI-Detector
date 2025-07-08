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

def download_file(url, filename):
    """Download a file from URL and save it locally"""
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Create downloads directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)
        
        filepath = os.path.join('downloads', filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def get_pdr_disposition(soup):
    """Check for PDR disposition status in Case Events table"""
    # Find the Case Events section - look for div containing "Case Events" text
    case_events_div = soup.find('div', class_=['panel-heading', 'panel-heading-content'], string=lambda text: text and 'Case Events' in text.strip())
    if not case_events_div:
        return None
    
    # Find the table with case events
    panel = case_events_div.parent
    table = panel.find('table', class_='rgMasterTable')
    if not table:
        return None
    
    # Look through table rows for PDR DISP
    rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 3:
            event_type = cells[1].get_text().strip()
            disposition = cells[2].get_text().strip()
            
            if 'PDR DISP' in event_type:
                if 'Granted' in disposition:
                    return 'granted'
                elif 'Refused' in disposition:
                    return 'refused'
    
    return None

def find_petition_document(soup):
    """Find PETITION document in Case Events table"""
    # Find the Case Events section - look for div containing "Case Events" text
    case_events_div = soup.find('div', class_=['panel-heading', 'panel-heading-content'], string=lambda text: text and 'Case Events' in text.strip())
    if not case_events_div:
        return None
    
    # Find the table with case events
    panel = case_events_div.parent
    table = panel.find('table', class_='rgMasterTable')
    if not table:
        return None
    
    # Look through table rows
    rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 4:
            # Check the document cell (4th column)
            doc_cell = cells[3]
            
            # Look for nested document table
            doc_table = doc_cell.find('table', class_='docGrid')
            if doc_table:
                doc_rows = doc_table.find_all('tr')
                for doc_row in doc_rows:
                    doc_cells = doc_row.find_all('td')
                    if len(doc_cells) >= 2:
                        # Check if this row contains PETITION
                        doc_type = doc_cells[1].get_text().strip()
                        if 'PETITION' in doc_type.upper():
                            # Get the link from the first cell
                            link = doc_cells[0].find('a')
                            if link and link.get('href'):
                                return link['href']
    
    return None

def find_appellant_brief(soup):
    """Find Appellant brief in Appellate Briefs table"""
    # Find the Appellate Briefs section - look for div containing "Appellate Briefs" text
    briefs_div = soup.find('div', class_=['panel-heading', 'panel-heading-content'], string=lambda text: text and 'Appellate Briefs' in text.strip())
    if not briefs_div:
        return None
    
    # Find the table with briefs
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
            
            # Look for "BRIEF FILED" by "Appellant"
            if event_type == "BRIEF FILED" and description == "Appellant":
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
                            if 'BRIEF' in doc_type.upper() and 'NOTICE' not in doc_type.upper():
                                # Get the link from the first cell
                                link = doc_cells[0].find('a')
                                if link and link.get('href'):
                                    return link['href']
    
    return None

def scrape_case_with_backoff(case_number, max_retries=3):
    """Scrape a single case with exponential backoff on errors"""
    for attempt in range(max_retries):
        try:
            return scrape_case(case_number)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                backoff_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Request failed for case PD-{case_number:04d}-24 (attempt {attempt + 1}), backing off for {backoff_time:.1f} seconds: {e}")
                time.sleep(backoff_time)
            else:
                print(f"Max retries exceeded for case PD-{case_number:04d}-24: {e}")
                return False
        except Exception as e:
            print(f"Unexpected error for case PD-{case_number:04d}-24: {e}")
            return False
    
    return False

def scrape_case(case_number):
    """Scrape a single case page for PDR and brief documents"""
    base_url = "https://search.txcourts.gov"
    case_url = f"{base_url}/Case.aspx?cn=PD-{case_number:04d}-24&coa=coscca"
    
    response = session.get(case_url, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for PDR disposition status
    pdr_disposition = get_pdr_disposition(soup)
    
    # Look for PETITION document
    petition_link = find_petition_document(soup)
    if petition_link:
        pdf_url = urljoin(base_url, petition_link)
        
        # Build filename with disposition status
        if pdr_disposition:
            filename = f"PD-{case_number:04d}-24 PDR ({pdr_disposition}).pdf"
        else:
            filename = f"PD-{case_number:04d}-24 PDR.pdf"
        
        download_file(pdf_url, filename)
    
    # Look for Appellant brief
    brief_link = find_appellant_brief(soup)
    if brief_link:
        pdf_url = urljoin(base_url, brief_link)
        filename = f"PD-{case_number:04d}-24 Brief.pdf"
        download_file(pdf_url, filename)
    
    print(f"Processed case PD-{case_number:04d}-24")
    return True

def main():
    """Main function to scrape all cases from 0001 to 1081"""
    print("Starting PDR document scraper...")
    print("This will process cases PD-0001-24 through PD-1081-24")
    
    failed_cases = []
    
    for case_num in range(1, 1082):  # 1 to 1081 inclusive
        success = scrape_case_with_backoff(case_num)
        if not success:
            failed_cases.append(case_num)
        
        # Add a small delay to be respectful to the server
        base_delay = 1.0
        jitter = random.uniform(0, 0.5)
        time.sleep(base_delay + jitter)
        
        # Progress indicator
        if case_num % 50 == 0:
            print(f"Progress: {case_num}/1081 cases processed")
    
    print("Scraping completed!")
    
    if failed_cases:
        print(f"\nFailed to process {len(failed_cases)} cases:")
        for case_num in failed_cases:
            print(f"  PD-{case_num:04d}-24")

if __name__ == "__main__":
    main() 