#!/./.venv/bin/python

import requests
from bs4 import BeautifulSoup

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

def debug_case(case_number):
    """Debug a single case to see what HTML structure we get"""
    base_url = "https://search.txcourts.gov"
    case_url = f"{base_url}/Case.aspx?cn=PD-{case_number:04d}-24&coa=coscca"
    
    print(f"Debugging case PD-{case_number:04d}-24")
    print(f"URL: {case_url}")
    
    try:
        response = session.get(case_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"Response status: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        
        # Look for any divs with panel-heading
        panel_headings = soup.find_all('div', class_='panel-heading')
        print(f"Found {len(panel_headings)} panel-heading divs")
        
        for i, heading in enumerate(panel_headings):
            print(f"  {i+1}. Classes: {heading.get('class')}")
            print(f"     Text: '{heading.get_text().strip()}'")
        
        # Look for any divs with panel-heading-content
        panel_heading_content = soup.find_all('div', class_='panel-heading-content')
        print(f"Found {len(panel_heading_content)} panel-heading-content divs")
        
        for i, heading in enumerate(panel_heading_content):
            print(f"  {i+1}. Classes: {heading.get('class')}")
            print(f"     Text: '{heading.get_text().strip()}'")
        
        # Look for text containing "Case Events" or "Appellate Briefs"
        case_events_text = soup.find_all(text=lambda text: text and 'Case Events' in text)
        print(f"Found {len(case_events_text)} elements containing 'Case Events'")
        
        for i, text in enumerate(case_events_text):
            parent = text.parent
            print(f"  {i+1}. Parent tag: {parent.name}")
            print(f"     Parent classes: {parent.get('class')}")
            print(f"     Text: '{text.strip()}'")
        
        briefs_text = soup.find_all(text=lambda text: text and 'Appellate Briefs' in text)
        print(f"Found {len(briefs_text)} elements containing 'Appellate Briefs'")
        
        for i, text in enumerate(briefs_text):
            parent = text.parent
            print(f"  {i+1}. Parent tag: {parent.name}")
            print(f"     Parent classes: {parent.get('class')}")
            print(f"     Text: '{text.strip()}'")
        
        # Look for any tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"  {i+1}. Classes: {table.get('class')}")
            print(f"     ID: {table.get('id')}")
        
        # Save a sample of the HTML for manual inspection
        with open(f'debug_case_{case_number:04d}.html', 'w') as f:
            f.write(str(soup.prettify()))
        print(f"HTML saved to debug_case_{case_number:04d}.html")
        
    except Exception as e:
        print(f"✗ Error processing case: {e}")

if __name__ == "__main__":
    # Debug a specific case
    debug_case(1) 