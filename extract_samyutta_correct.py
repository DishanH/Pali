"""
Correct PDF Extraction Script for Saṃyutta Nikāya
Extracts Pali text and creates JSON files for each saṃyutta (collection)
Structure: Vagga (major section) > Saṃyutta (collection) > Suttas
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

class SamyuttaSaṃyuttaExtractor:
    """Extract Pali text from Saṃyutta Nikāya PDF and create saṃyutta JSON files"""
    
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
    
    def detect_samyuttas(self, text: str) -> List[Dict]:
        """
        Detect saṃyuttas (collections) from the text
        Saṃyuttas are marked like: "1. Devatāsaṃyuttaṃ"
        """
        print("\nDetecting saṃyuttas (collections) from PDF...")
        
        lines = text.split('\n')
        samyuttas = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Pattern: number, dot, space, name ending with saṃyuttaṃ
            match = re.match(r'^(\d+)\.\s+(.+saṃyuttaṃ)$', line_stripped, re.IGNORECASE)
            
            if match:
                samyutta_num = int(match.group(1))
                samyutta_title = match.group(2)
                
                # Generate ID
                samyutta_id = f"sn.{self.book_config['vagga_num']}.{len(samyuttas) + 1}"
                
                samyuttas.append({
                    'id': samyutta_id,
                    'number': samyutta_num,
                    'title': samyutta_title,
                    'line_num': i
                })
                print(f"  ✓ Found saṃyutta {samyutta_num}: {samyutta_title} ({samyutta_id})")
        
        print(f"\n✓ Detected {len(samyuttas)} saṃyuttas")
        return samyuttas
    
    def find_samyutta_boundaries(self, text: str, samyuttas: List[Dict]) -> List[Tuple[int, int, Dict]]:
        """Find the start and end positions of each saṃyutta"""
        print("\nFinding saṃyutta boundaries...")
        
        lines = text.split('\n')
        boundaries = []
        
        for i, samyutta_info in enumerate(samyuttas):
            start_line = samyutta_info['line_num']
            
            # Find end (start of next saṃyutta or end of file)
            if i + 1 < len(samyuttas):
                end_line = samyuttas[i + 1]['line_num']
            else:
                end_line = len(lines)
            
            print(f"  ✓ {samyutta_info['title']}: lines {start_line} to {end_line}")
            boundaries.append((start_line, end_line, samyutta_info))
        
        return boundaries
    
    def extract_suttas_from_samyutta(self, samyutta_text: str) -> List[Dict]:
        """
        Extract suttas (sections) from a saṃyutta
        Structure varies but typically:
        - Vagga title like "1. Naḷavaggo"
        - Sutta title like "1. Oghataraṇasuttaṃ" or "617-621. Rūpaanabhisamayādisuttapañcakaṃ"
        - Numbered sections like "1. Evaṃ me sutaṃ..." or "617-621. Content..."
        """
        lines = samyutta_text.split('\n')
        suttas = []
        current_sutta = None
        current_lines = []
        current_sutta_title = None
        current_vagga_title = None
        
        # Skip the first line (saṃyutta title)
        start_idx = 1
        
        for i in range(start_idx, len(lines)):
            line_stripped = lines[i].strip()
            
            if not line_stripped:
                continue
            
            # Check for vagga title within saṃyutta: number, dot, space, name ending with vaggo
            vaggo_match = re.match(r'^(\d+)\.\s+(.+vaggo)$', line_stripped, re.IGNORECASE)
            if vaggo_match:
                current_vagga_title = vaggo_match.group(2)
                continue
            
            # Check for sutta title with range: "617-621. Rūpaanabhisamayādisuttapañcakaṃ"
            sutta_range_match = re.match(r'^(\d+)-(\d+)\.\s+(.+suttaṃ|.+suttapañcakaṃ|.+suttadasakaṃ)$', line_stripped, re.IGNORECASE)
            # Check for sutta title: number, dot, space, name ending with suttaṃ
            sutta_match = re.match(r'^(\d+)\.\s+(.+suttaṃ)$', line_stripped, re.IGNORECASE)
            
            if sutta_range_match:
                # This is a sutta title with range, save it for the next section
                current_sutta_title = sutta_range_match.group(3)
                continue
            elif sutta_match:
                # This is a regular sutta title, save it for the next section
                current_sutta_title = sutta_match.group(2)
                continue
            
            # Check for section number with range: "617-621. Content..."
            section_range_match = re.match(r'^(\d+)-(\d+)\.\s+(.+)', line_stripped)
            # Check for section number: number, dot, space, then content
            section_match = re.match(r'^(\d+)\.\s+(.+)', line_stripped)
            
            if section_range_match:
                # Save previous sutta
                if current_sutta is not None:
                    current_sutta['pali'] = ' '.join(current_lines)
                    suttas.append(current_sutta)
                
                start_num = int(section_range_match.group(1))
                end_num = int(section_range_match.group(2))
                number_range = f"{start_num}-{end_num}"
                rest_of_line = section_range_match.group(3)
                
                current_sutta = {
                    "number": start_num,
                    "numberRange": number_range,
                    "pali": "",
                    "english": "",
                    "sinhala": "",
                    "paliTitle": current_sutta_title if current_sutta_title else "",
                    "vagga": current_vagga_title if current_vagga_title else ""
                }
                current_lines = [rest_of_line]
                current_sutta_title = None  # Reset after using
            elif section_match:
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
                    "paliTitle": current_sutta_title if current_sutta_title else "",
                    "vagga": current_vagga_title if current_vagga_title else ""
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
    
    def create_samyutta_json(self, samyutta_info: Dict, samyutta_text: str) -> Dict:
        """Create a JSON structure for a saṃyutta"""
        suttas = self.extract_suttas_from_samyutta(samyutta_text)
        
        samyutta_json = {
            "id": samyutta_info['id'],
            "title": {
                "pali": samyutta_info['title'],
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
        
        return samyutta_json
    
    def save_samyutta_json(self, samyutta_info: Dict, samyutta_json: Dict):
        """Save a saṃyutta JSON to a file"""
        filename = f"{samyutta_info['id']}-{samyutta_info['title']}.json"
        output_path = os.path.join(self.output_dir, "chapters", filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(samyutta_json, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved: {filename} ({len(samyutta_json['sections'])} suttas)")
    
    def create_book_json(self, samyuttas: List[Dict]):
        """Create a book.json file with metadata about all saṃyuttas"""
        book_json = {
            "name": self.book_config['name'],
            "title": {
                "pali": self.book_config['pali_title'],
                "english": self.book_config.get('english_title', ''),
                "sinhala": self.book_config.get('sinhala_title', '')
            },
            "chapters": [
                {
                    "id": samyutta['id'],
                    "title": {
                        "pali": samyutta['title'],
                        "english": "",
                        "sinhala": ""
                    }
                }
                for samyutta in samyuttas
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
        
        print("\n[4/6] Detecting saṃyuttas (collections)...")
        samyuttas = self.detect_samyuttas(self.full_text)
        
        print("\n[5/6] Finding saṃyutta boundaries...")
        boundaries = self.find_samyutta_boundaries(self.full_text, samyuttas)
        
        print("\n[6/6] Creating saṃyutta JSON files...")
        lines = self.full_text.split('\n')
        
        for start_line, end_line, samyutta_info in boundaries:
            samyutta_lines = lines[start_line:end_line]
            samyutta_text = '\n'.join(samyutta_lines)
            
            samyutta_json = self.create_samyutta_json(samyutta_info, samyutta_text)
            self.save_samyutta_json(samyutta_info, samyutta_json)
        
        self.create_book_json(samyuttas)
        
        print("\n" + "=" * 70)
        print("✅ Extraction Complete!")
        print("=" * 70)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Chapter JSONs: {os.path.join(self.output_dir, 'chapters')}")
        print(f"Book metadata: {os.path.join(self.output_dir, 'book.json')}")


def main():
    """Main entry point - for testing single file"""
    
    book_config = {
        'name': 'Sagāthāvaggo',
        'pali_title': 'Sagāthāvaggo',
        'english_title': '',
        'sinhala_title': '',
        'vagga_num': 1,  # First vagga of Saṃyutta
    }
    
    pdf_path = r"Saṃyuttanikāyo\pdfs\Sagāthāvaggo.pdf"
    output_dir = r"Saṃyuttanikāyo\Sagāthāvaggo"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return
    
    extractor = SamyuttaSaṃyuttaExtractor(pdf_path, output_dir, book_config)
    extractor.process()


if __name__ == "__main__":
    main()

