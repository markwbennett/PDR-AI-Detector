#!/./.venv/bin/python

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
import random

def download_file(url, filename):
    """Download a file from URL and save it locally"""
    try:
        response = requests.get(url, timeout=30)
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
    """Check for PDR disposition status in Case Events"""
    case_events_panel = soup.find('div', class_='panel-heading panel-heading-content', string='Case Events')
    if not case_events_panel:
        return None
    
    # Find the parent panel and look for PDR DISP entries
    panel = case_events_panel.parent
    rows = panel.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 2:
            # Check if any cell contains "PDR DISP"
            for i, cell in enumerate(cells):
                if 'PDR DISP' in cell.get_text().upper():
                    # Check the next cell for disposition
                    if i + 1 < len(cells):
                        next_cell_text = cells[i + 1].get_text().strip()
                        if 'GRANTED' in next_cell_text.upper():
                            return 'granted'
                        elif 'REFUSED' in next_cell_text.upper():
                            return 'refused'
    
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
    
    response = requests.get(case_url, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for PDR disposition status
    pdr_disposition = get_pdr_disposition(soup)
    
    # Look for Case Events section
    case_events_panel = soup.find('div', class_='panel-heading panel-heading-content', string='Case Events')
    if case_events_panel:
        # Find the parent panel and look for PETITION documents
        panel = case_events_panel.parent
        petition_links = panel.find_all('a', href=True)
        
        for link in petition_links:
            # Check if this is a petition document link
            next_cell = link.parent.find_next_sibling('td')
            if next_cell and 'PETITION' in next_cell.get_text().upper():
                pdf_url = urljoin(base_url, link['href'])
                
                # Build filename with disposition status
                if pdr_disposition:
                    filename = f"PD-{case_number:04d}-24 PDR ({pdr_disposition}).pdf"
                else:
                    filename = f"PD-{case_number:04d}-24 PDR.pdf"
                
                download_file(pdf_url, filename)
                break
    
    # Look for Appellate Briefs section
    briefs_panel = soup.find('div', class_='panel-heading panel-heading-content', string='Appellate Briefs')
    if briefs_panel:
        # Find the parent panel and look for brief documents
        panel = briefs_panel.parent
        brief_rows = panel.find_all('tr')
        
        for row in brief_rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                # Check if this is a "BRIEF FILED" row with "Appellant"
                event_type = cells[1].get_text().strip()
                description = cells[2].get_text().strip()
                
                if event_type == "BRIEF FILED" and description == "Appellant":
                    # Look for the brief document link (not the notice)
                    doc_cell = cells[3] if len(cells) > 3 else None
                    if doc_cell:
                        doc_links = doc_cell.find_all('a', href=True)
                        for link in doc_links:
                            # Check if this is the brief (not notice)
                            next_cell = link.parent.find_next_sibling('td')
                            if next_cell and 'BRIEF' in next_cell.get_text().upper() and 'NOTICE' not in next_cell.get_text().upper():
                                pdf_url = urljoin(base_url, link['href'])
                                filename = f"PD-{case_number:04d}-24 Brief.pdf"
                                download_file(pdf_url, filename)
                                break
    
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