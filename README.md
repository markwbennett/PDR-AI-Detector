# PDR AI Detector

A Python web scraper for downloading Petition for Discretionary Review (PDR) documents and appellate briefs from the Texas Courts website.

## Overview

This tool automatically scrapes cases PD-0001-24 through PD-1081-24 from the Texas Court of Criminal Appeals search system, downloading:

- **PDR Documents**: Petition for Discretionary Review files with disposition status (granted/refused)
- **Appellate Briefs**: Appellant briefs when available

## Features

- **Automated Scraping**: Processes 1,081 cases automatically
- **Disposition Detection**: Identifies granted/refused PDR status from case events
- **Error Handling**: Exponential backoff for failed requests with retry logic
- **Rate Limiting**: Respectful delays between requests to avoid overwhelming the server
- **Browser Emulation**: Uses proper headers to avoid 403 errors
- **Progress Tracking**: Shows progress every 50 cases and reports failed cases

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/markwbennett/PDR-AI-Detector.git
   cd "PDR AI Detector"
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Interactive Launcher

Run the main script for an interactive menu:

```bash
./main.py
```

Options:
1. **Run full scraper** - Process all 1,081 cases (PD-0001-24 to PD-1081-24)
2. **Test scraper** - Test on sample cases (1, 50, 100, 451, 500, 1000)
3. **Exit**

### Direct Execution

**Run the full scraper directly:**
```bash
./scraper.py
```

**Test the scraper:**
```bash
./test_scraper.py
```

## File Structure

```
PDR AI Detector/
├── main.py              # Interactive launcher
├── scraper.py           # Main scraping logic
├── test_scraper.py      # Test script for sample cases
├── requirements.txt     # Python dependencies
├── downloads/           # Downloaded PDF files (created automatically)
│   ├── PD-0001-24 PDR (refused).pdf
│   ├── PD-0451-24 PDR (granted).pdf
│   ├── PD-0451-24 Brief.pdf
│   └── ...
└── .venv/              # Virtual environment
```

## Output Files

Downloaded files are saved to the `downloads/` directory with naming convention:

- **PDR Documents:**
  - `PD-{number}-24 PDR (granted).pdf` - For granted petitions
  - `PD-{number}-24 PDR (refused).pdf` - For refused petitions  
  - `PD-{number}-24 PDR.pdf` - For petitions without disposition

- **Appellate Briefs:**
  - `PD-{number}-24 Brief.pdf` - For appellant briefs

## How It Works

1. **Case URL Generation**: Creates URLs for each case (PD-0001-24 to PD-1081-24)
2. **HTML Parsing**: Uses BeautifulSoup to parse case pages
3. **Section Detection**: Finds "Case Events" and "Appellate Briefs" sections
4. **Document Extraction**: Locates PETITION documents and appellant briefs in nested tables
5. **Disposition Detection**: Checks for "PDR DISP" events with "Granted"/"Refused" status
6. **File Download**: Downloads PDFs with appropriate filenames

## Error Handling

- **Exponential Backoff**: Retries failed requests with increasing delays
- **Rate Limiting**: 1-1.5 second delays between requests
- **Session Management**: Maintains persistent connections
- **Progress Reporting**: Shows failed cases at completion

## Dependencies

- `requests>=2.25.0` - HTTP requests
- `beautifulsoup4>=4.9.0` - HTML parsing
- `lxml>=4.6.0` - XML/HTML parser backend

## Technical Details

### Web Scraping Strategy

- **Browser Headers**: Mimics Chrome browser to avoid detection
- **Session Persistence**: Maintains cookies and connections
- **Nested Table Parsing**: Handles complex HTML structure with `docGrid` tables
- **Text Matching**: Flexible text matching for section headers with whitespace

### Rate Limiting

- Base delay: 1.0 second between requests
- Random jitter: 0-0.5 seconds additional delay
- Exponential backoff: 2^attempt + random(0,1) seconds for retries

## Example Usage

```python
# Test a single case
python test_scraper.py

# Run full scraper
python scraper.py

# Use interactive launcher
python main.py
```

## Troubleshooting

**403 Errors**: The scraper includes browser headers to avoid these. If you encounter 403 errors, the site may have additional anti-bot measures.

**Network Timeouts**: The scraper includes 30-second timeouts and retry logic. Persistent timeouts may indicate network issues.

**Missing Documents**: Not all cases have PDR documents or appellate briefs. The scraper will report what it finds.

## Legal Notice

This tool is for educational and research purposes. Please respect the Texas Courts website's terms of service and use responsibly. The scraper includes respectful delays to avoid overwhelming the server.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for educational purposes. Please ensure compliance with applicable laws and website terms of service. 