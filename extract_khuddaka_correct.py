"""
Correct PDF Extraction Script for Khuddaka Nikāya
Extracts Pali text and creates JSON files for each vagga/chapter
Khuddaka has varied structures - this handles the most common patterns
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

class KhuddakaExtractor:
    """Extract Pali text from Khuddaka Nikāya PDFs and create chapter JSON files"""
    
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
    
    def detect_chapters(self, text: str) -> List[Dict]:
        """
        Detect chapters from the text
        Khuddaka uses various structures:
        - Vaggas like "1. Yamakavaggo"
        - Nipātas like "1. Uragavaggo"
        - Sometimes just numbered sections
        """
        print("\nDetecting chapters from PDF...")
        
        lines = text.split('\n')
        chapters = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Pattern 1: Vaggo - "1. Yamakavaggo"
            match1 = re.match(r'^(\d+)\.\s+(.+vaggo)$', line_stripped, re.IGNORECASE)
            # Pattern 2: Nipāta - "1. Uragavaggo" (Sutta Nipāta style)
            match2 = re.match(r'^(\d+)\.\s+(.+nipāta)$', line_stripped, re.IGNORECASE)
            # Pattern 3: Vatthu - "1. Upakāravatthu" (for Vimānavatthu, Petavatthu)
            match3 = re.match(r'^(\d+)\.\s+(.+vatthu)$', line_stripped, re.IGNORECASE)
            # Pattern 4: Named sections - look for titles with specific keywords
            match4 = re.match(r'^(\d+)\.\s+([A-ZĀĪŪṄÑṬḌṆḶṂ].+)$', line_stripped)
            
            match = match1 or match2 or match3
            if match:
                chapter_num = int(match.group(1))
                chapter_title = match.group(2)
                
                # Generate ID
                chapter_id = f"{self.book_config['id_prefix']}.{len(chapters) + 1}"
                
                chapters.append({
                    'id': chapter_id,
                    'number': chapter_num,
                    'title': chapter_title,
                    'line_num': i
                })
                print(f"  ✓ Found chapter {chapter_num}: {chapter_title} ({chapter_id})")
            elif match4 and self.book_config.get('use_generic_chapters', False):
                # For texts without clear vaggo/nipāta markers
                chapter_num = int(match4.group(1))
                chapter_title = match4.group(2)
                
                chapter_id = f"{self.book_config['id_prefix']}.{len(chapters) + 1}"
                
                chapters.append({
                    'id': chapter_id,
                    'number': chapter_num,
                    'title': chapter_title,
                    'line_num': i
                })
                print(f"  ✓ Found chapter {chapter_num}: {chapter_title} ({chapter_id})")
        
        # If no chapters detected, treat entire text as one chapter
        if not chapters:
            print("  ⚠️  No chapter markers found. Creating single chapter.")
            chapters.append({
                'id': f"{self.book_config['id_prefix']}.1",
                'number': 1,
                'title': self.book_config['name'],
                'line_num': 0
            })
        
        print(f"\n✓ Detected {len(chapters)} chapters")
        return chapters
    
    def find_chapter_boundaries(self, text: str, chapters: List[Dict]) -> List[Tuple[int, int, Dict]]:
        """Find the start and end positions of each chapter"""
        print("\nFinding chapter boundaries...")
        
        lines = text.split('\n')
        boundaries = []
        
        for i, chapter_info in enumerate(chapters):
            start_line = chapter_info['line_num']
            
            # Find end (start of next chapter or end of file)
            if i + 1 < len(chapters):
                end_line = chapters[i + 1]['line_num']
            else:
                end_line = len(lines)
            
            print(f"  ✓ {chapter_info['title']}: lines {start_line} to {end_line}")
            boundaries.append((start_line, end_line, chapter_info))
        
        return boundaries
    
    def extract_sections_from_chapter(self, chapter_text: str) -> List[Dict]:
        """
        Extract numbered sections from a chapter
        Handles various formats:
        - Numbered verses/sections
        - Sutta-like structures
        """
        lines = chapter_text.split('\n')
        sections = []
        current_section = None
        current_lines = []
        current_title = None
        
        # Skip the first line (chapter title)
        start_idx = 1
        
        for i in range(start_idx, len(lines)):
            line_stripped = lines[i].strip()
            
            if not line_stripped:
                continue
            
            # Check for sutta/section title (optional)
            title_match = re.match(r'^(\d+)\.\s+(.+suttaṃ)$', line_stripped, re.IGNORECASE)
            if title_match:
                current_title = title_match.group(2)
                continue
            
            # Check for numbered section/verse
            section_match = re.match(r'^(\d+)\.\s*(.*)$', line_stripped)
            
            if section_match:
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
                    "sinhala": "",
                    "paliTitle": current_title if current_title else ""
                }
                
                # Include the rest of the line if present
                if rest_of_line:
                    current_lines = [rest_of_line]
                else:
                    current_lines = []
                    
                current_title = None  # Reset after using
            else:
                # Regular content line
                if current_section is not None:
                    current_lines.append(line_stripped)
                elif not sections:
                    # First section without number - create section 1
                    current_section = {
                        "number": 1,
                        "pali": "",
                        "english": "",
                        "sinhala": "",
                        "paliTitle": ""
                    }
                    current_lines = [line_stripped]
        
        # Save the last section
        if current_section is not None:
            current_section['pali'] = ' '.join(current_lines)
            sections.append(current_section)
        
        return sections
    
    def create_chapter_json(self, chapter_info: Dict, chapter_text: str) -> Dict:
        """Create a JSON structure for a chapter"""
        sections = self.extract_sections_from_chapter(chapter_text)
        
        chapter_json = {
            "id": chapter_info['id'],
            "title": {
                "pali": chapter_info['title'],
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
        
        return chapter_json
    
    def save_chapter_json(self, chapter_info: Dict, chapter_json: Dict):
        """Save a chapter JSON to a file"""
        filename = f"{chapter_info['id']}-{chapter_info['title']}.json"
        output_path = os.path.join(self.output_dir, "chapters", filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chapter_json, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved: {filename} ({len(chapter_json['sections'])} sections)")
    
    def create_book_json(self, chapters: List[Dict]):
        """Create a book.json file with metadata about all chapters"""
        book_json = {
            "name": self.book_config['name'],
            "title": {
                "pali": self.book_config['pali_title'],
                "english": self.book_config.get('english_title', ''),
                "sinhala": self.book_config.get('sinhala_title', '')
            },
            "chapters": [
                {
                    "id": chapter['id'],
                    "title": {
                        "pali": chapter['title'],
                        "english": "",
                        "sinhala": ""
                    }
                }
                for chapter in chapters
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
        
        print("\n[4/6] Detecting chapters...")
        chapters = self.detect_chapters(self.full_text)
        
        print("\n[5/6] Finding chapter boundaries...")
        boundaries = self.find_chapter_boundaries(self.full_text, chapters)
        
        print("\n[6/6] Creating chapter JSON files...")
        lines = self.full_text.split('\n')
        
        for start_line, end_line, chapter_info in boundaries:
            chapter_lines = lines[start_line:end_line]
            chapter_text = '\n'.join(chapter_lines)
            
            chapter_json = self.create_chapter_json(chapter_info, chapter_text)
            self.save_chapter_json(chapter_info, chapter_json)
        
        self.create_book_json(chapters)
        
        print("\n" + "=" * 70)
        print("✅ Extraction Complete!")
        print("=" * 70)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Chapter JSONs: {os.path.join(self.output_dir, 'chapters')}")
        print(f"Book metadata: {os.path.join(self.output_dir, 'book.json')}")


def main():
    """Main entry point - for testing single file"""
    
    book_config = {
        'name': 'Dhammapadapāḷi',
        'pali_title': 'Dhammapadapāḷi',
        'english_title': '',
        'sinhala_title': '',
        'id_prefix': 'dhp',  # Dhammapada chapters
        'use_generic_chapters': False,
    }
    
    pdf_path = r"Khuddakanikāye\pdfs\Dhammapadapāḷi.pdf"
    output_dir = r"Khuddakanikāye\Dhammapadapāḷi"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return
    
    extractor = KhuddakaExtractor(pdf_path, output_dir, book_config)
    extractor.process()


if __name__ == "__main__":
    main()

