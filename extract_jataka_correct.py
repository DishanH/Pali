"""
Correct PDF Extraction Script for Jātakapāḷi
Extracts Pali text and creates JSON files for each vagga
Jātakapāḷi has a unique 3-level structure: Nipāta > Vagga > Jātaka
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

class JatakaExtractor:
    """Extract Pali text from Jātakapāḷi PDFs and create vagga JSON files"""
    
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
    
    def detect_structure(self, text: str) -> List[Dict]:
        """
        Detect nipātas as chapters, with vaggas as subsections
        Returns a list of nipātas with their vaggas
        """
        print("\nDetecting structure from PDF...")
        
        lines = text.split('\n')
        nipatas = []
        current_nipata = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Detect Nipāta: "1. Ekakanipāto" or "17. Cattālīsanipāto"
            nipata_match = re.match(r'^(\d+)\.\s+(.+nipāto)$', line_stripped, re.IGNORECASE)
            if nipata_match:
                nipata_num = int(nipata_match.group(1))
                nipata_title = nipata_match.group(2)
                
                # Create new nipāta chapter
                nipata_id = f"{self.book_config['id_prefix']}.{len(nipatas) + 1}"
                current_nipata = {
                    'id': nipata_id,
                    'nipata_number': nipata_num,
                    'nipata_title': nipata_title,
                    'line_num': i,
                    'vaggas': [],
                    'is_nipata_chapter': nipata_num >= 17  # Later nipatas don't have vaggas
                }
                nipatas.append(current_nipata)
                print(f"  ✓ Found Nipāta {nipata_num}: {nipata_title} ({nipata_id})")
                continue
            
            # Detect Vagga: "1. Apaṇṇakavaggo" (only for early nipatas)
            vagga_match = re.match(r'^(\d+)\.\s+(.+vaggo)$', line_stripped, re.IGNORECASE)
            if vagga_match and current_nipata and not current_nipata['is_nipata_chapter']:
                vagga_num = int(vagga_match.group(1))
                vagga_title = vagga_match.group(2)
                
                current_nipata['vaggas'].append({
                    'vagga_number': vagga_num,
                    'vagga_title': vagga_title,
                    'line_num': i
                })
                print(f"    ✓ Found Vagga {vagga_num}: {vagga_title}")
        
        print(f"\n✓ Detected {len(nipatas)} nipātas")
        return nipatas
    
    def find_nipata_boundaries(self, text: str, nipatas: List[Dict]) -> List[Tuple[int, int, Dict]]:
        """Find the start and end positions of each nipāta"""
        print("\nFinding nipāta boundaries...")
        
        lines = text.split('\n')
        boundaries = []
        
        for i, nipata_info in enumerate(nipatas):
            start_line = nipata_info['line_num']
            
            # Find end (start of next nipāta or end of file)
            if i + 1 < len(nipatas):
                end_line = nipatas[i + 1]['line_num']
            else:
                end_line = len(lines)
            
            print(f"  ✓ {nipata_info['nipata_title']}: lines {start_line} to {end_line}")
            boundaries.append((start_line, end_line, nipata_info))
        
        return boundaries
    
    def extract_jatakas_from_nipata(self, nipata_text: str, nipata_info: Dict, is_nipata_chapter: bool = False) -> List[Dict]:
        """
        Extract individual Jātaka stories from a nipāta
        Handles vaggas within the nipāta and adds vaggaTitle to first section of each vagga
        """
        lines = nipata_text.split('\n')
        sections = []
        current_jataka_title = None
        current_jataka_number = None
        current_section = None
        current_lines = []
        current_vagga_title = None
        vaggas = nipata_info.get('vaggas', [])
        vagga_line_nums = {v['line_num']: v['vagga_title'] for v in vaggas}
        
        # Skip header lines
        start_idx = 0
        for idx, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('Namo') or line_stripped == 'Khuddakanikāye':
                continue
            if line_stripped == 'Jātakapāḷi' or line_stripped.endswith('bhāgo)'):
                continue
            # Skip nipāta title
            if re.match(r'^\d+\.\s+.+nipāto$', line_stripped, re.IGNORECASE):
                start_idx = idx + 1
                break
            # If we find a numbered item, start from there
            if re.match(r'^\d+\.', line_stripped):
                start_idx = idx
                break
        
        for i in range(start_idx, len(lines)):
            line_stripped = lines[i].strip()
            
            if not line_stripped:
                continue
            
            # Check if this line is a vagga title
            vagga_match = re.match(r'^(\d+)\.\s+(.+vaggo)$', line_stripped, re.IGNORECASE)
            if vagga_match and not is_nipata_chapter:
                current_vagga_title = vagga_match.group(2)
                continue
            
            # For later volumes: "521. Tesakuṇajātakaṃ (1)"
            if is_nipata_chapter:
                jataka_with_num_match = re.match(r'^(\d+)\.\s+(.+jātakaṃ)\s*\((\d+)\)$', line_stripped, re.IGNORECASE)
                if jataka_with_num_match:
                    # Save previous section before starting new jātaka
                    if current_section is not None:
                        current_section['pali'] = ' '.join(current_lines)
                        sections.append(current_section)
                        current_section = None
                        current_lines = []
                    
                    current_jataka_number = int(jataka_with_num_match.group(1))
                    current_jataka_title = jataka_with_num_match.group(2)
                    continue
            
            # For early volumes: "1. Apaṇṇakajātakaṃ" or "151. Rājovādajātakaṃ (2-1-1)"
            jataka_title_match = re.match(r'^(\d+)\.\s+(.+jātakaṃ(?:\s*\([^)]+\))?)$', line_stripped, re.IGNORECASE)
            if jataka_title_match and not is_nipata_chapter:
                # Save previous section before starting new one
                if current_section is not None:
                    current_section['pali'] = ' '.join(current_lines)
                    sections.append(current_section)
                    current_section = None
                    current_lines = []
                
                jataka_num = jataka_title_match.group(1)
                jataka_name = jataka_title_match.group(2)
                # Keep the full title with number: "151. Rājovādajātakaṃ (2-1-1)"
                current_jataka_title = f"{jataka_num}. {jataka_name}"
                continue
            
            # Check for numbered section (the actual verse/content)
            # Only create sections if we have a jataka title OR we're already processing sections
            section_match = re.match(r'^(\d+)\.\s*(.*)$', line_stripped)
            if section_match and (current_jataka_title or current_section is not None):
                # Save previous section
                if current_section is not None:
                    current_section['pali'] = ' '.join(current_lines)
                    sections.append(current_section)
                
                section_number = int(section_match.group(1))
                rest_of_line = section_match.group(2)
                
                current_section = {
                    "number": section_number,
                    "pali": "",
                    "english": "",
                    "sinhala": ""
                }
                
                # Add paliTitle only if we have one (and only once per jātaka)
                if current_jataka_title:
                    current_section["paliTitle"] = current_jataka_title
                
                # Add nipataTitle only to the first section
                if len(sections) == 0:
                    current_section["nipataTitle"] = nipata_info['nipata_title']
                
                # Add vaggaTitle to first section of each vagga
                if current_vagga_title:
                    current_section["vaggaTitle"] = current_vagga_title
                    current_vagga_title = None  # Reset after using
                
                # Include the rest of the line if present
                if rest_of_line:
                    current_lines = [rest_of_line]
                else:
                    current_lines = []
                
                # Reset title after using it (for both early and later volumes)
                current_jataka_title = None
            else:
                # Regular content line
                if current_section is not None:
                    current_lines.append(line_stripped)
        
        # Save the last section
        if current_section is not None:
            current_section['pali'] = ' '.join(current_lines)
            sections.append(current_section)
        
        return sections
    
    def create_nipata_json(self, nipata_info: Dict, nipata_text: str) -> Dict:
        """Create a JSON structure for a nipāta chapter"""
        is_nipata_chapter = nipata_info.get('is_nipata_chapter', False)
        sections = self.extract_jatakas_from_nipata(
            nipata_text, 
            nipata_info,
            is_nipata_chapter
        )
        
        nipata_json = {
            "id": nipata_info['id'],
            "title": {
                "pali": nipata_info['nipata_title'],
                "english": "",
                "sinhala": ""
            },
            "sections": sections,
            "footer": {
                "pali": "",
                "english": "",
                "sinhala": ""
            }
        }
        
        return nipata_json
    
    def save_nipata_json(self, nipata_info: Dict, nipata_json: Dict):
        """Save a nipāta JSON to a file"""
        filename = f"{nipata_info['id']}-{nipata_info['nipata_title']}.json"
        output_path = os.path.join(self.output_dir, "chapters", filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(nipata_json, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved: {filename} ({len(nipata_json['sections'])} jātakas)")
    
    def create_book_json(self, nipatas: List[Dict]):
        """Create a book.json file with metadata about all nipātas"""
        book_json = {
            "name": self.book_config['name'],
            "title": {
                "pali": self.book_config['pali_title'],
                "english": self.book_config.get('english_title', ''),
                "sinhala": self.book_config.get('sinhala_title', '')
            },
            "chapters": [
                {
                    "id": nipata['id'],
                    "title": {
                        "pali": nipata['nipata_title'],
                        "english": "",
                        "sinhala": ""
                    }
                }
                for nipata in nipatas
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
        
        print("\n[4/6] Detecting structure (Nipāta > Vagga)...")
        nipatas = self.detect_structure(self.full_text)
        
        print("\n[5/6] Finding nipāta boundaries...")
        boundaries = self.find_nipata_boundaries(self.full_text, nipatas)
        
        print("\n[6/6] Creating nipāta JSON files...")
        lines = self.full_text.split('\n')
        
        for start_line, end_line, nipata_info in boundaries:
            nipata_lines = lines[start_line:end_line]
            nipata_text = '\n'.join(nipata_lines)
            
            nipata_json = self.create_nipata_json(nipata_info, nipata_text)
            self.save_nipata_json(nipata_info, nipata_json)
        
        self.create_book_json(nipatas)
        
        print("\n" + "=" * 70)
        print("✅ Extraction Complete!")
        print("=" * 70)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Vagga JSONs: {os.path.join(self.output_dir, 'chapters')}")
        print(f"Book metadata: {os.path.join(self.output_dir, 'book.json')}")


def main():
    """Main entry point - for testing single file"""
    
    book_config = {
        'name': 'Jātakapāḷi',
        'pali_title': 'Jātakapāḷi',
        'english_title': '',
        'sinhala_title': '',
        'id_prefix': 'ja',
    }
    
    pdf_path = r"Khuddakanikāye\pdfs\Jātakapāḷi_1.pdf"
    output_dir = r"Khuddakanikāye\Jātakapāḷi"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return
    
    extractor = JatakaExtractor(pdf_path, output_dir, book_config)
    extractor.process()


if __name__ == "__main__":
    main()
