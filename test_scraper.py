#!/./.venv/bin/python

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

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

def test_single_case(case_number):
    """Test scraping a single case to verify the logic works"""
    base_url = "https://search.txcourts.gov"
    case_url = f"{base_url}/Case.aspx?cn=PD-{case_number:04d}-24&coa=coscca"
    
    print(f"Testing case PD-{case_number:04d}-24")
    print(f"URL: {case_url}")
    
    try:
        response = requests.get(case_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for PDR disposition status
        pdr_disposition = get_pdr_disposition(soup)
        if pdr_disposition:
            print(f"✓ Found PDR disposition: {pdr_disposition}")
        else:
            print("- No PDR disposition found")
        
        # Check for Case Events section
        case_events_panel = soup.find('div', class_='panel-heading panel-heading-content', string='Case Events')
        if case_events_panel:
            print("✓ Found Case Events section")
            
            # Find the parent panel and look for PETITION documents
            panel = case_events_panel.parent
            petition_links = panel.find_all('a', href=True)
            
            petition_found = False
            for link in petition_links:
                next_cell = link.parent.find_next_sibling('td')
                if next_cell and 'PETITION' in next_cell.get_text().upper():
                    if pdr_disposition:
                        filename = f"PD-{case_number:04d}-24 PDR ({pdr_disposition}).pdf"
                    else:
                        filename = f"PD-{case_number:04d}-24 PDR.pdf"
                    print(f"✓ Found PETITION document: {link['href']}")
                    print(f"  Would save as: {filename}")
                    petition_found = True
                    break
            
            if not petition_found:
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