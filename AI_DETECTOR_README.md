# AI Detector for PDR Documents

This script analyzes PDR (Petition for Discretionary Review) documents to detect potential AI-generated content using Claude 3.5 Sonnet.

## Setup

1. Install dependencies:
   ```bash
   ./.venv/bin/pip install -r requirements.txt
   ```

2. Set up your Anthropic API key in `.env`:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

## Usage

Run the AI detector:
```bash
./.venv/bin/python ai_detector.py
```

Or use the main menu option 3.

## How it works

1. **Document Processing**: Extracts text from all PDF files in the `downloads/` directory
2. **AI Analysis**: Sends each document to Claude 3.5 Sonnet with a prompt asking:
   - How much of the document was written by an LLM? (percentage)
   - How confident are you of that assessment? (confidence percentage)
   - What are the specific tells or indicators of AI generation?

3. **Filtering**: Only documents where Claude is >50% confident that >5% was AI-generated are included in the report

4. **HTML Report**: Generates `ai_detection_report.html` with:
   - Summary of flagged documents
   - For each flagged document: filename, AI percentage, confidence level, and specific indicators
   - Sorted by AI percentage (highest first)

## Output

The script creates an HTML report (`ai_detection_report.html`) listing documents that meet the criteria, with detailed analysis of AI indicators and confidence levels.

## API Costs

This script makes API calls to Anthropic's Claude 3.5 Sonnet. Each PDF document requires one API call. Monitor your usage and costs accordingly. 