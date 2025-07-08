# Changelog

All notable changes to the PDR AI Detector project will be documented in this file.

## [1.0.0] - 2024-01-XX

### Added
- Initial release of PDR AI Detector
- Web scraper for Texas Courts PDR documents (PD-0001-24 to PD-1081-24)
- Automated detection of PDR disposition status (granted/refused)
- Download functionality for PETITION documents and appellant briefs
- Interactive launcher with menu system
- Test script for sample cases
- Error handling with exponential backoff
- Rate limiting to respect server resources
- Browser header emulation to avoid 403 errors
- Progress tracking and reporting
- Comprehensive documentation

### Technical Features
- BeautifulSoup HTML parsing
- Nested table structure handling
- Session management for persistent connections
- Flexible text matching for section headers
- Virtual environment setup
- Proper gitignore configuration

### Files Added
- `main.py` - Interactive launcher
- `scraper.py` - Main scraping logic  
- `test_scraper.py` - Test script
- `requirements.txt` - Python dependencies
- `README.md` - Comprehensive documentation
- `.gitignore` - Git ignore rules
- `CHANGELOG.md` - Version history

### Dependencies
- requests>=2.25.0
- beautifulsoup4>=4.9.0
- lxml>=4.6.0 