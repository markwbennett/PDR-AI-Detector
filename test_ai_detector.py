#!/./.venv/bin/python

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import anthropic
from dotenv import load_dotenv
import PyPDF2

# Load environment variables
load_dotenv()

class PDRAIDetectorTest:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.downloads_dir = Path("downloads")
        self.results = []
        
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text content from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
            return ""
    
    def analyze_document(self, text: str, filename: str) -> Optional[Dict]:
        """Send document to Claude for AI detection analysis"""
        if not text.strip():
            return None
            
        prompt = f"""Please analyze this legal document for AI-generated content.

Document: {filename}

Text:
{text}

Please answer these specific questions:
1. How much of this document was written by an LLM? (Give a percentage estimate)
2. How confident are you of that assessment? (Give a percentage confidence level)
3. What are the specific tells or indicators that suggest AI generation?

Please format your response as JSON with the following structure:
{{
    "percentage_ai_generated": <number>,
    "confidence_percentage": <number>,
    "tells": ["tell1", "tell2", "tell3"]
}}

Focus on legal writing patterns, repetitive phrasing, unusual word choices, overly formal language, and other indicators common in AI-generated legal documents."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.content[0].text
            print(f"    Raw response: {response_text[:200]}...")
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    result['filename'] = filename
                    return result
                except json.JSONDecodeError as e:
                    print(f"    JSON decode error for {filename}: {e}")
                    print(f"    Attempted to parse: {json_match.group()}")
                    return None
            else:
                print(f"    No JSON found in response for {filename}")
                print(f"    Full response: {response_text}")
                return None
                
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
            return None
    
    def should_include_in_report(self, result: Dict) -> bool:
        """Check if document meets criteria for inclusion in HTML report"""
        confidence = result.get('confidence_percentage', 0)
        ai_percentage = result.get('percentage_ai_generated', 0)
        
        return confidence > 50 and ai_percentage > 5
    
    def generate_html_report(self, flagged_documents: List[Dict]) -> str:
        """Generate HTML report of flagged documents"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>PDR AI Detection Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .document {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 5px; }}
        .filename {{ font-weight: bold; color: #333; font-size: 18px; }}
        .stats {{ margin: 10px 0; }}
        .stat {{ display: inline-block; margin-right: 20px; padding: 5px 10px; background-color: #e9e9e9; border-radius: 3px; }}
        .tells {{ margin-top: 10px; }}
        .tell {{ background-color: #fff3cd; padding: 3px 8px; margin: 2px; border-radius: 3px; display: inline-block; }}
        .summary {{ background-color: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PDR AI Detection Test Report (First 10 Files)</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Criteria: Documents where Claude is >50% confident that >5% was AI-generated</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>{len(flagged_documents)}</strong> documents flagged as potentially containing AI-generated content</p>
    </div>
"""
        
        for doc in sorted(flagged_documents, key=lambda x: x['percentage_ai_generated'], reverse=True):
            html += f"""
    <div class="document">
        <div class="filename">{doc['filename']}</div>
        <div class="stats">
            <span class="stat">AI Generated: {doc['percentage_ai_generated']}%</span>
            <span class="stat">Confidence: {doc['confidence_percentage']}%</span>
        </div>
        <div class="tells">
            <strong>AI Indicators:</strong><br>
"""
            for tell in doc.get('tells', []):
                html += f'            <span class="tell">{tell}</span>\n'
            
            html += """        </div>
    </div>
"""
        
        html += """
</body>
</html>"""
        
        return html
    
    def run_test_analysis(self):
        """Main function to run AI detection on first 10 PDR files"""
        if not self.downloads_dir.exists():
            print(f"Downloads directory {self.downloads_dir} not found")
            return
        
        # Get first 10 PDF files
        pdf_files = list(self.downloads_dir.glob("*.pdf"))[:10]
        total_files = len(pdf_files)
        
        print(f"Found {total_files} PDF files to analyze (first 10)")
        
        flagged_documents = []
        all_results = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"Processing {i}/{total_files}: {pdf_file.name}")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_file)
            if not text.strip():
                print(f"  No text extracted from {pdf_file.name}")
                continue
            
            # Analyze with Claude
            result = self.analyze_document(text, pdf_file.name)
            if result:
                all_results.append(result)
                print(f"  AI: {result['percentage_ai_generated']}%, Confidence: {result['confidence_percentage']}%")
                
                # Check if should be included in report
                if self.should_include_in_report(result):
                    flagged_documents.append(result)
                    print(f"  FLAGGED for report")
            else:
                print(f"  Analysis failed")
        
        # Print summary of all results
        print(f"\n=== TEST RESULTS SUMMARY ===")
        print(f"Total documents analyzed: {len(all_results)}")
        print(f"Documents flagged: {len(flagged_documents)}")
        print(f"\nAll results:")
        for result in all_results:
            flag_status = "FLAGGED" if self.should_include_in_report(result) else "not flagged"
            print(f"  {result['filename']}: {result['percentage_ai_generated']}% AI, {result['confidence_percentage']}% confidence ({flag_status})")
        
        # Generate HTML report
        html_report = self.generate_html_report(flagged_documents)
        report_path = Path("ai_detection_test_report.html")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"\nTest report generated: {report_path}")

def main():
    detector = PDRAIDetectorTest()
    
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY") == "your_api_key_here":
        print("Please set your ANTHROPIC_API_KEY in the .env file")
        return
    
    detector.run_test_analysis()

if __name__ == "__main__":
    main() 