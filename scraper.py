#!/./.venv/bin/python

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin

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

def scrape_case(case_number):
    """Scrape a single case page for PDR and brief documents"""
    base_url = "https://search.txcourts.gov"
    case_url = f"{base_url}/Case.aspx?cn=PD-{case_number:04d}-24&coa=coscca"
    
    try:
        response = requests.get(case_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
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
        
    except Exception as e:
        print(f"Error processing case PD-{case_number:04d}-24: {e}")

def main():
    """Main function to scrape all cases from 0001 to 1081"""
    print("Starting PDR document scraper...")
    print("This will process cases PD-0001-24 through PD-1081-24")
    
    for case_num in range(1, 1082):  # 1 to 1081 inclusive
        scrape_case(case_num)
        
        # Add a small delay to be respectful to the server
        time.sleep(1)
        
        # Progress indicator
        if case_num % 50 == 0:
            print(f"Progress: {case_num}/1081 cases processed")
    
    print("Scraping completed!")

if __name__ == "__main__":
    main() 