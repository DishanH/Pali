"""
Correct PDF Extraction Script for Majjhima Nikāya
Extracts Pali text and creates JSON files for each vagga (chapter)
Similar to Aṅguttara structure but adapted for Majjhima's organization
"""

import sys
import fitz  # PyMuPDF
import json
import re
import os
from typing import List, Dict, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

class MajjhimaVaggaExtractor:
    """Extract Pali text from Majjhima Nikāya PDF and create vagga (chapter) JSON files"""
    
    def __init__(self, pdf_path: str, output_dir: str, book_config: Dict):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.book_config = book_config
        self.full_text = ""
        
        self.remove_patterns = [
            r'Page \d+ sur \d+',
            r'www\.tipitaka\.org',
            r'Vipassana.*Research Institute',
        ]
        
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
        """Save the full extracted text"""
        filename = f"{self.book_config['name']}_pali_extracted.txt"
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✓ Saved full text to: {output_path}")
    
    def detect_vaggas(self, text: str) -> List[Dict]:
        """
        Detect vaggas (chapters) from the text
        Majjhima vaggas are marked like: "1. Mūlapariyāyavaggo"
        """
        print("\nDetecting vaggas (chapters) from PDF...")
        
        lines = text.split('\n')
        vaggas = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Pattern: number, dot, space, name ending with vaggo
            match = re.match(r'^(\d+)\.\s+(.+vaggo)$', line_stripped, re.IGNORECASE)
            
            if match:
                vagga_num = int(match.group(1))
                vagga_title = match.group(2)
                
                # Generate ID
                vagga_id = f"mn.{self.book_config['book_num']}.{len(vaggas) + 1}"
                
                vaggas.append({
                    'id': vagga_id,
                    'number': vagga_num,
                    'title': vagga_title,
                    'line_num': i
                })
                print(f"  ✓ Found vagga {vagga_num}: {vagga_title} ({vagga_id})")
        
        print(f"\n✓ Detected {len(vaggas)} vaggas")
        return vaggas
    
    def find_vagga_boundaries(self, text: str, vaggas: List[Dict]) -> List[Tuple[int, int, Dict]]:
        """Find the start and end positions of each vagga"""
        print("\nFinding vagga boundaries...")
        
        lines = text.split('\n')
        boundaries = []
        
        for i, vagga_info in enumerate(vaggas):
            start_line = vagga_info['line_num']
            
            # Find end (start of next vagga or end of file)
            if i + 1 < len(vaggas):
                end_line = vaggas[i + 1]['line_num']
            else:
                end_line = len(lines)
            
            print(f"  ✓ {vagga_info['title']}: lines {start_line} to {end_line}")
            boundaries.append((start_line, end_line, vagga_info))
        
        return boundaries
    
    def extract_suttas_from_vagga(self, vagga_text: str) -> List[Dict]:
        """
        Extract suttas (sections) from a vagga
        Suttas in Majjhima are marked like: "1. Mūlapariyāyasuttaṃ"
        followed by numbered sections like "1. Evaṃ me sutaṃ..."
        """
        lines = vagga_text.split('\n')
        suttas = []
        current_sutta = None
        current_lines = []
        current_sutta_title = None
        
        # Skip the first line (vagga title)
        start_idx = 1
        
        for i in range(start_idx, len(lines)):
            line_stripped = lines[i].strip()
            
            if not line_stripped:
                continue
            
            # Check for sutta title: number, dot, space, name ending with suttaṃ
            sutta_match = re.match(r'^(\d+)\.\s+(.+suttaṃ)$', line_stripped, re.IGNORECASE)
            
            if sutta_match:
                # This is a sutta title, save it for the next section
                current_sutta_title = sutta_match.group(2)
                continue
            
            # Check for section number: number, dot, space, then content
            section_match = re.match(r'^(\d+)\.\s+(.+)', line_stripped)
            
            if section_match:
                # Save previous sutta
                if current_sutta is not None:
                    current_sutta['pali'] = ' '.join(current_lines)
                    suttas.append(current_sutta)
                
                section_number = int(section_match.group(1))
                rest_of_line = section_match.group(2)
                
                current_sutta = {
                    "number": section_number,
                    "pali": "",
                    "english": "",
                    "sinhala": "",
                    "paliTitle": current_sutta_title if current_sutta_title else ""
                }
                current_lines = [rest_of_line]
                current_sutta_title = None  # Reset after using
            else:
                # Regular content line
                if current_sutta is not None:
                    current_lines.append(line_stripped)
        
        # Save the last sutta
        if current_sutta is not None:
            current_sutta['pali'] = ' '.join(current_lines)
            suttas.append(current_sutta)
        
        return suttas
    
    def create_vagga_json(self, vagga_info: Dict, vagga_text: str) -> Dict:
        """Create a JSON structure for a vagga (chapter)"""
        suttas = self.extract_suttas_from_vagga(vagga_text)
        
        vagga_json = {
            "id": vagga_info['id'],
            "title": {
                "pali": vagga_info['title'],
                "english": "",
                "sinhala": ""
            },
            "sections": suttas,  # Suttas are the sections
            "footer": {
                "pali": "",
                "english": "",
                "sinhala": ""
            }
        }
        
        return vagga_json
    
    def save_vagga_json(self, vagga_info: Dict, vagga_json: Dict):
        """Save a vagga JSON to a file"""
        filename = f"{vagga_info['id']}-{vagga_info['title']}.json"
        output_path = os.path.join(self.output_dir, "chapters", filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(vagga_json, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved: {filename} ({len(vagga_json['sections'])} suttas)")
    
    def create_book_json(self, vaggas: List[Dict]):
        """Create a book.json file with metadata about all vaggas"""
        book_json = {
            "name": self.book_config['name'],
            "title": {
                "pali": self.book_config['pali_title'],
                "english": self.book_config.get('english_title', ''),
                "sinhala": self.book_config.get('sinhala_title', '')
            },
            "chapters": [
                {
                    "id": vagga['id'],
                    "title": {
                        "pali": vagga['title'],
                        "english": "",
                        "sinhala": ""
                    }
                }
                for vagga in vaggas
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
        
        print("\n[1/6] Extracting text from PDF...")
        self.full_text = self.extract_text_from_pdf()
        
        print("\n[2/6] Cleaning text...")
        self.full_text = self.clean_text(self.full_text)
        
        print("\n[3/6] Saving full extracted text...")
        self.save_full_text(self.full_text)
        
        print("\n[4/6] Detecting vaggas (chapters)...")
        vaggas = self.detect_vaggas(self.full_text)
        
        print("\n[5/6] Finding vagga boundaries...")
        boundaries = self.find_vagga_boundaries(self.full_text, vaggas)
        
        print("\n[6/6] Creating vagga (chapter) JSON files...")
        lines = self.full_text.split('\n')
        
        for start_line, end_line, vagga_info in boundaries:
            vagga_lines = lines[start_line:end_line]
            vagga_text = '\n'.join(vagga_lines)
            
            vagga_json = self.create_vagga_json(vagga_info, vagga_text)
            self.save_vagga_json(vagga_info, vagga_json)
        
        self.create_book_json(vaggas)
        
        print("\n" + "=" * 70)
        print("✅ Extraction Complete!")
        print("=" * 70)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Chapter JSONs: {os.path.join(self.output_dir, 'chapters')}")
        print(f"Book metadata: {os.path.join(self.output_dir, 'book.json')}")


def main():
    """Main entry point - for testing single file"""
    
    book_config = {
        'name': 'Mūlapaṇṇāsapāḷi',
        'pali_title': 'Mūlapaṇṇāsapāḷi',
        'english_title': '',
        'sinhala_title': '',
        'book_num': 1,  # First book of Majjhima
    }
    
    pdf_path = r"Majjhimanikāye\pdfs\Mūlapaṇṇāsapāḷi.pdf"
    output_dir = r"Majjhimanikāye\Mūlapaṇṇāsapāḷi"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return
    
    extractor = MajjhimaVaggaExtractor(pdf_path, output_dir, book_config)
    extractor.process()


if __name__ == "__main__":
    main()

