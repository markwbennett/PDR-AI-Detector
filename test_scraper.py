#!/./.venv/bin/python

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

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

def get_pdr_disposition(soup):
    """Check for PDR disposition status in Case Events table"""
    # Find the Case Events section
    case_events_div = soup.find('div', class_='panel-heading panel-heading-content', string='Case Events')
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
    # Find the Case Events section
    case_events_div = soup.find('div', class_='panel-heading panel-heading-content', string='Case Events')
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

def test_single_case(case_number):
    """Test scraping a single case to verify the logic works"""
    base_url = "https://search.txcourts.gov"
    case_url = f"{base_url}/Case.aspx?cn=PD-{case_number:04d}-24&coa=coscca"
    
    print(f"Testing case PD-{case_number:04d}-24")
    print(f"URL: {case_url}")
    
    try:
        response = session.get(case_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for PDR disposition status
        pdr_disposition = get_pdr_disposition(soup)
        if pdr_disposition:
            print(f"✓ Found PDR disposition: {pdr_disposition}")
        else:
            print("- No PDR disposition found")
        
        # Check for Case Events section
        case_events_div = soup.find('div', class_='panel-heading panel-heading-content', string='Case Events')
        if case_events_div:
            print("✓ Found Case Events section")
            
            # Look for PETITION document
            petition_link = find_petition_document(soup)
            if petition_link:
                if pdr_disposition:
                    filename = f"PD-{case_number:04d}-24 PDR ({pdr_disposition}).pdf"
                else:
                    filename = f"PD-{case_number:04d}-24 PDR.pdf"
                print(f"✓ Found PETITION document: {petition_link}")
                print(f"  Would save as: {filename}")
            else:
                print("✗ No PETITION document found")
        else:
            print("✗ Case Events section not found")
        
        # Check for Appellate Briefs section
        briefs_panel = soup.find('div', class_='panel-heading panel-heading-content', string='Appellate Briefs')
        if briefs_panel:
            print("✓ Found Appellate Briefs section")
            
            # Find the parent panel and look for brief documents
            panel = briefs_panel.parent
            brief_rows = panel.find_all('tr')
            
            brief_found = False
            for row in brief_rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    event_type = cells[1].get_text().strip()
                    description = cells[2].get_text().strip()
                    
                    if event_type == "BRIEF FILED" and description == "Appellant":
                        print(f"✓ Found BRIEF FILED by Appellant")
                        
                        # Look for the brief document link
                        doc_cell = cells[3] if len(cells) > 3 else None
                        if doc_cell:
                            doc_links = doc_cell.find_all('a', href=True)
                            for link in doc_links:
                                next_cell = link.parent.find_next_sibling('td')
                                if next_cell and 'BRIEF' in next_cell.get_text().upper() and 'NOTICE' not in next_cell.get_text().upper():
                                    print(f"✓ Found Brief document: {link['href']}")
                                    print(f"  Would save as: PD-{case_number:04d}-24 Brief.pdf")
                                    brief_found = True
                                    break
                        break
            
            if not brief_found:
                print("✗ No Appellant Brief found")
        else:
            print("✗ Appellate Briefs section not found")
        
    except Exception as e:
        print(f"✗ Error processing case: {e}")

if __name__ == "__main__":
    # Test with a few case numbers
    test_cases = [1, 50, 100, 500, 1000]
    
    for case_num in test_cases:
        test_single_case(case_num)
        print("-" * 50) 