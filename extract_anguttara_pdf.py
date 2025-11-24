"""
Specialized PDF Extraction Script for Aṅguttara Nikāya
Extracts Pali text from PDF and creates structured JSON files for each sutta
"""

import sys
import fitz  # PyMuPDF
import json
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

class AnguttaraPDFExtractor:
    """Extract Pali text from Aṅguttara Nikāya PDF and create sutta JSON files"""
    
    def __init__(self, pdf_path: str, output_dir: str, book_config: Dict):
        """
        Initialize the extractor
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save the extracted JSON files
            book_config: Dictionary with book metadata
        """
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.book_config = book_config
        self.full_text = ""
        
        # Patterns to remove (metadata)
        self.remove_patterns = [
            r'Page \d+ sur \d+',
            r'www\.tipitaka\.org',
            r'Vipassana.*Research Institute',
        ]
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_text_from_pdf(self) -> str:
        """Extract text from PDF"""
        print(f"Opening PDF: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        
        all_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                all_text.append(text)
            
            if (page_num + 1) % 10 == 0:
                print(f"  Processed {page_num + 1}/{len(doc)} pages...")
        
        print(f"✓ Extracted text from {len(doc)} pages")
        doc.close()
        
        return '\n'.join(all_text)
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        print("Cleaning text...")
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            for pattern in self.remove_patterns:
                line = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
            
            if not line or re.match(r'^\s*\d+\s*$', line):
                continue
            
            cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines)
        print(f"✓ Cleaned text: {len(cleaned_lines)} lines")
        return cleaned_text
    
    def save_full_text(self, text: str):
        """Save the full extracted text to a file"""
        filename = f"{self.book_config['name']}_pali_extracted.txt"
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✓ Saved full text to: {output_path}")
    
    def detect_suttas(self, text: str) -> List[Dict]:
        """
        Detect individual suttas from the text
        
        In Aṅguttara Nikāya, suttas are marked like:
        1. Mettāsuttaṃ
        2. Paññāsuttaṃ
        etc.
        """
        print("\nDetecting suttas from PDF...")
        
        lines = text.split('\n')
        suttas = []
        sutta_counter = 1
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Look for sutta titles: number, dot, space, name ending with suttaṃ
            match = re.match(r'^(\d+)\.\s+(.+suttaṃ)$', line_stripped, re.IGNORECASE)
            if match:
                sutta_num = int(match.group(1))
                sutta_title = match.group(2)
                
                # Generate ID based on book's starting AN number
                an_number = self.book_config['starting_an'] + len(suttas)
                sutta_id = f"an{self.book_config['nipata_num']}.{an_number}"
                
                suttas.append({
                    'id': sutta_id,
                    'number': sutta_num,
                    'title': sutta_title,
                    'an_number': an_number,
                    'line_num': i
                })
                print(f"  ✓ Found sutta {sutta_num}: {sutta_title} ({sutta_id})")
        
        print(f"\n✓ Detected {len(suttas)} suttas")
        return suttas
    
    def find_sutta_boundaries(self, text: str, suttas: List[Dict]) -> List[Tuple[int, int, Dict]]:
        """Find the start and end positions of each sutta"""
        print("\nFinding sutta boundaries...")
        
        lines = text.split('\n')
        boundaries = []
        
        for i, sutta_info in enumerate(suttas):
            start_line = sutta_info['line_num']
            
            # Find end (start of next sutta or end of file)
            if i + 1 < len(suttas):
                end_line = suttas[i + 1]['line_num']
            else:
                end_line = len(lines)
            
            print(f"  ✓ {sutta_info['title']}: lines {start_line} to {end_line}")
            boundaries.append((start_line, end_line, sutta_info))
        
        return boundaries
    
    def extract_sections_from_sutta(self, sutta_text: str) -> List[Dict]:
        """
        Extract numbered sections from a sutta
        
        Sections are numbered like:
        1. Evaṃ me sutaṃ...
        2. ''Aṭṭhime, bhikkhave...
        """
        lines = sutta_text.split('\n')
        sections = []
        current_section = None
        current_lines = []
        
        # Skip the first line (sutta title)
        start_idx = 1
        
        for i in range(start_idx, len(lines)):
            line_stripped = lines[i].strip()
            
            if not line_stripped:
                continue
            
            # Check for numbered section start
            section_match = re.match(r'^(\d+)\.\s+(.+)', line_stripped)
            
            if section_match:
                # Save previous section
                if current_section is not None:
                    current_section['pali'] = ' '.join(current_lines)
                    sections.append(current_section)
                
                section_num = int(section_match.group(1))
                rest_of_line = section_match.group(2)
                
                current_section = {
                    "number": section_num,
                    "pali": "",
                    "english": "",
                    "sinhala": "",
                    "paliTitle": ""
                }
                current_lines = [rest_of_line]
            else:
                # Regular content line
                if current_section is not None:
                    current_lines.append(line_stripped)
        
        # Save the last section
        if current_section is not None:
            current_section['pali'] = ' '.join(current_lines)
            sections.append(current_section)
        
        return sections
    
    def create_sutta_json(self, sutta_info: Dict, sutta_text: str) -> Dict:
        """Create a JSON structure for a sutta"""
        sections = self.extract_sections_from_sutta(sutta_text)
        
        sutta_json = {
            "id": sutta_info['id'],
            "title": {
                "pali": sutta_info['title'],
                "english": "",
                "sinhala": ""
            },
            "sections": sections
        }
        
        return sutta_json
    
    def save_sutta_json(self, sutta_info: Dict, sutta_json: Dict):
        """Save a sutta JSON to a file"""
        filename = f"{sutta_info['id']}-{sutta_info['title']}.json"
        output_path = os.path.join(self.output_dir, "suttas", filename)
        
        # Create suttas directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sutta_json, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved: {filename} ({len(sutta_json['sections'])} sections)")
    
    def create_book_json(self, suttas: List[Dict]):
        """Create a book.json file with metadata about all suttas"""
        book_json = {
            "name": self.book_config['name'],
            "title": {
                "pali": self.book_config['pali_title'],
                "english": self.book_config.get('english_title', ''),
                "sinhala": self.book_config.get('sinhala_title', '')
            },
            "suttas": [
                {
                    "id": sutta['id'],
                    "title": {
                        "pali": sutta['title'],
                        "english": "",
                        "sinhala": ""
                    }
                }
                for sutta in suttas
            ]
        }
        
        output_path = os.path.join(self.output_dir, "book.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(book_json, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Saved book metadata: book.json")
    
    def process(self):
        """Main processing method"""
        print("=" * 70)
        print(f"{self.book_config['name']} PDF Extraction")
        print("=" * 70)
        
        # Step 1: Extract text
        print("\n[1/6] Extracting text from PDF...")
        self.full_text = self.extract_text_from_pdf()
        
        # Step 2: Clean text
        print("\n[2/6] Cleaning text...")
        self.full_text = self.clean_text(self.full_text)
        
        # Step 3: Save full text
        print("\n[3/6] Saving full extracted text...")
        self.save_full_text(self.full_text)
        
        # Step 4: Detect suttas
        print("\n[4/6] Detecting suttas...")
        suttas = self.detect_suttas(self.full_text)
        
        # Step 5: Find sutta boundaries
        print("\n[5/6] Finding sutta boundaries...")
        boundaries = self.find_sutta_boundaries(self.full_text, suttas)
        
        # Step 6: Process each sutta
        print("\n[6/6] Creating sutta JSON files...")
        lines = self.full_text.split('\n')
        
        for start_line, end_line, sutta_info in boundaries:
            sutta_lines = lines[start_line:end_line]
            sutta_text = '\n'.join(sutta_lines)
            
            # Create sutta JSON
            sutta_json = self.create_sutta_json(sutta_info, sutta_text)
            
            # Save sutta JSON
            self.save_sutta_json(sutta_info, sutta_json)
        
        # Create book.json
        self.create_book_json(suttas)
        
        print("\n" + "=" * 70)
        print("✅ Extraction Complete!")
        print("=" * 70)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Sutta JSONs: {os.path.join(self.output_dir, 'suttas')}")
        print(f"Book metadata: {os.path.join(self.output_dir, 'book.json')}")


def main():
    """Main entry point - for testing single file"""
    
    book_config = {
        'name': 'Aṭṭhakanipātapāḷi',
        'pali_title': 'Aṭṭhakanipātapāḷi',
        'english_title': '',
        'sinhala_title': '',
        'nipata_num': 8,  # This is the "Book of Eights"
        'starting_an': 1,  # AN 8.1, 8.2, etc.
    }
    
    pdf_path = r"Aṅguttaranikāyo\pdfs\Aṭṭhakanipātapāḷi.pdf"
    output_dir = r"Aṅguttaranikāyo\Aṭṭhakanipātapāḷi"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return
    
    extractor = AnguttaraPDFExtractor(pdf_path, output_dir, book_config)
    extractor.process()


if __name__ == "__main__":
    main()
