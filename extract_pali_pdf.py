"""
Generalized PDF Extraction Script for Dīgha Nikāya
Extracts Pali text from PDF and creates structured JSON files for each chapter
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

class PaliPDFExtractor:
    """Extract Pali text from Dīgha Nikāya PDF and create chapter JSON files"""
    
    def __init__(self, pdf_path: str, output_dir: str, book_config: Dict):
        """
        Initialize the extractor
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save the extracted JSON files
            book_config: Dictionary with book metadata and chapter information
        """
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.book_config = book_config
        self.full_text = ""
        self.full_text_with_formatting = []  # Store text with formatting info
        self.renumber_sections = book_config.get('renumber_sections', True)  # Renumber sections from 1 for each chapter
        
        # Patterns to remove (metadata)
        self.remove_patterns = [
            r'Page \d+ sur \d+',  # Page numbers like "Page 1 sur 144"
            r'www\.tipitaka\.org',  # Website URL
            r'Vipassana.*Research Institute',  # Organization (with any content between)
        ]
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_text_from_pdf(self) -> Tuple[str, List[Dict]]:
        """
        Extract text from PDF with formatting information
        
        Returns:
            Tuple of (plain_text, formatted_blocks)
            - plain_text: Simple text extraction
            - formatted_blocks: List of dicts with text and formatting info (bold, size, etc.)
        """
        print(f"Opening PDF: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        
        all_text = []
        formatted_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text with layout preservation
            text = page.get_text("text")
            if text.strip():
                all_text.append(text)
            
            # Extract with formatting information for detecting bold titles
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        is_bold = False
                        font_size = 0
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            # Check if font name contains "Bold"
                            if "bold" in span["font"].lower():
                                is_bold = True
                            font_size = max(font_size, span["size"])
                        
                        if line_text.strip():
                            formatted_blocks.append({
                                "text": line_text.strip(),
                                "is_bold": is_bold,
                                "font_size": font_size,
                                "page": page_num
                            })
            
            if (page_num + 1) % 10 == 0:
                print(f"  Processed {page_num + 1}/{len(doc)} pages...")
        
        print(f"✓ Extracted text from {len(doc)} pages")
        doc.close()
        
        return '\n'.join(all_text), formatted_blocks
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing metadata and normalizing
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        print("Cleaning text...")
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Remove metadata patterns
            for pattern in self.remove_patterns:
                line = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
            
            # Skip if line became empty or is just numbers
            if not line or re.match(r'^\s*\d+\s*$', line):
                continue
            
            cleaned_lines.append(line)
        
        # Join with single newline
        cleaned_text = '\n'.join(cleaned_lines)
        
        print(f"✓ Cleaned text: {len(cleaned_lines)} lines")
        return cleaned_text
    
    def save_full_text(self, text: str):
        """
        Save the full extracted text to a file
        
        Args:
            text: The text to save
        """
        filename = f"{self.book_config['name']}_pali_extracted.txt"
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✓ Saved full text to: {output_path}")
    
    def auto_detect_chapters(self, text: str) -> List[Dict]:
        """
        Automatically detect chapters from the text
        
        Args:
            text: The full cleaned text
            
        Returns:
            List of detected chapters with metadata
        """
        print("\nAuto-detecting chapters from PDF...")
        
        lines = text.split('\n')
        chapters = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Look for numbered sutta titles like "1. Brahmajālasuttaṃ"
            match = re.match(r'^(\d+)\.\s+(\w+suttaṃ)', line_stripped)
            if match:
                chapter_num = int(match.group(1))
                chapter_title = match.group(2)
                
                # Generate ID based on book's starting DN number
                dn_number = self.book_config['starting_dn'] + len(chapters)
                chapter_id = f"dn{dn_number}"
                
                chapters.append({
                    'id': chapter_id,
                    'number': chapter_num,
                    'title': chapter_title,
                    'dn_number': dn_number
                })
                print(f"  ✓ Found chapter {chapter_num}: {chapter_title} (DN {dn_number})")
        
        print(f"\n✓ Auto-detected {len(chapters)} chapters")
        return chapters
    
    def find_chapter_boundaries(self, text: str, chapters: List[Dict]) -> List[Tuple[int, int, Dict]]:
        """
        Find the start and end positions of each chapter in the text
        
        Args:
            text: The full cleaned text
            chapters: List of chapter metadata
            
        Returns:
            List of tuples: (start_line, end_line, chapter_info)
        """
        print("\nFinding chapter boundaries...")
        
        lines = text.split('\n')
        boundaries = []
        
        for i, chapter_info in enumerate(chapters):
            chapter_title = chapter_info['title']
            chapter_num = chapter_info['number']
            
            # Find chapter start - look for pattern like "1. Brahmajālasuttaṃ"
            start_line = None
            for line_num, line in enumerate(lines):
                # More precise matching: number, dot, space, then exact title
                if re.match(r'^' + str(chapter_num) + r'\.\s+' + re.escape(chapter_title) + r'\s*$', line.strip()):
                    start_line = line_num
                    print(f"  ✓ Chapter {chapter_num} ({chapter_title})")
                    print(f"    Start: line {line_num}")
                    break
            
            if start_line is None:
                print(f"  ✗ Warning: Could not find start of chapter: {chapter_title}")
                continue
            
            # Find chapter end (start of next chapter or end of file)
            end_line = len(lines)
            if i + 1 < len(chapters):
                next_chapter = chapters[i + 1]
                next_chapter_title = next_chapter['title']
                next_chapter_num = next_chapter['number']
                
                for line_num in range(start_line + 1, len(lines)):
                    line = lines[line_num].strip()
                    # Look for next chapter's numbered title
                    if re.match(r'^' + str(next_chapter_num) + r'\.\s+' + re.escape(next_chapter_title) + r'\s*$', line):
                        end_line = line_num
                        print(f"    End: line {line_num - 1} (next chapter starts at {line_num})")
                        break
            else:
                print(f"    End: line {end_line - 1} (last chapter)")
            
            boundaries.append((start_line, end_line, chapter_info))
        
        return boundaries
    
    def detect_section_title(self, line: str, formatted_blocks: List[Dict] = None) -> Optional[str]:
        """
        Detect if a line is a section title (paliTitle)
        
        Section titles are typically:
        - Short lines (< 80 chars)
        - Bold text (if formatting available)
        - End with certain patterns (vatthu, kathā, vaṇṇanā, sīlaṃ, etc.)
        - Are standalone (not part of a sentence)
        - Do NOT start with quotes or contain punctuation
        
        Args:
            line: The line to check
            formatted_blocks: Optional list of formatted text blocks for bold detection
            
        Returns:
            The title if detected, None otherwise
        """
        line = line.strip()
        
        # Skip if too long, empty, or starts with quotes (not a title)
        if len(line) > 100 or len(line) == 0 or line.startswith("'") or line.startswith('"'):
            return None
        
        # Skip if it starts with a number (likely a numbered section)
        if re.match(r'^\d+\.', line):
            return None
        
        # Skip if it contains sentence-like structures (but allow "niṭṭhitaṃ" endings)
        if ',' in line or ';' in line or '?' in line:
            return None
        
        # Allow lines ending with "niṭṭhitaṃ." (completion markers)
        if not line.endswith('niṭṭhitaṃ.'):
            # Skip if it contains periods in the middle
            if '.' in line.rstrip('.'):
                return None
        
        # Check if this line is bold in the formatted blocks
        is_bold = False
        if formatted_blocks:
            for block in formatted_blocks:
                # More flexible matching - check if line is contained in block or vice versa
                if (line in block['text'] or block['text'] in line) and block['is_bold']:
                    is_bold = True
                    break
        
        # Check for common section title patterns
        title_patterns = [
            r'vatthu$',
            r'kathā$',
            r'vaṇṇanā$',
            r'vaṇṇā$',
            r'dhammā$',
            r'dhammatā$',
            r'lakkhaṇā$',
            r'paṭisaṃyutta',
            r'nidāna',
            r'vagga$',
            r'ñāṇa$',
            r'samādhi$',
            r'sīlaṃ$',  # Important: matches Cūḷasīlaṃ, Majjhimasīlaṃ, Mahāsīlaṃ
            r'sīla$',
            r'ṭhiti$',
            r'vimokkha$',
            r'paññatti$',
            r'niṭṭhitaṃ\.$',  # Matches completion markers like "Cūḷasīlaṃ niṭṭhitaṃ."
        ]
        
        for pattern in title_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return line
        
        # If it's bold and not too long, consider it a title
        # Relaxed criteria: allow up to 6 words
        if is_bold and len(line) < 80 and line.count(' ') <= 6:
            # Additional check: should not look like a sentence
            # (sentences typically have many common words)
            common_sentence_words = ['evaṃ', 'kho', 'bhagavā', 'bhikkhave', 'āha', 'vā', 'ca']
            word_count = sum(1 for word in common_sentence_words if word in line.lower())
            if word_count < 2:  # If less than 2 common sentence words, likely a title
                return line
        
        return None
    
    def extract_sections_from_chapter(self, chapter_text: str, chapter_lines_start: int) -> List[Dict]:
        """
        Extract sections from a chapter text
        
        Each section is identified by a number pattern like "1. ", "2. ", etc.
        
        Args:
            chapter_text: The text of a single chapter
            chapter_lines_start: Starting line number in the full text (for formatted_blocks lookup)
            
        Returns:
            List of section dictionaries
        """
        lines = chapter_text.split('\n')
        sections = []
        current_section = None
        current_lines = []
        pending_pali_title = None
        renumbered_section_counter = 1  # For renumbering sections
        
        # Skip the first line if it's the chapter title (numbered suttaṃ)
        start_idx = 0
        if lines and re.match(r'^\d+\.\s+\w+suttaṃ', lines[0].strip()):
            start_idx = 1
        
        for i in range(start_idx, len(lines)):
            line_stripped = lines[i].strip()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Check if this is a section title (should come before numbered sections)
            detected_title = self.detect_section_title(line_stripped, self.full_text_with_formatting)
            if detected_title:
                pending_pali_title = detected_title
                continue
            
            # Check if this is a numbered section start (e.g., "1. ", "2. ", etc.)
            section_match = re.match(r'^(\d+)\.\s+(.+)', line_stripped)
            
            if section_match:
                # Save previous section if exists
                if current_section is not None:
                    current_section['pali'] = ' '.join(current_lines)
                    sections.append(current_section)
                
                # Get section number from text
                original_section_num = int(section_match.group(1))
                rest_of_line = section_match.group(2)
                
                # Use renumbered counter if enabled, otherwise use original
                if self.renumber_sections:
                    section_num = renumbered_section_counter
                    renumbered_section_counter += 1
                else:
                    section_num = original_section_num
                
                current_section = {
                    "number": section_num,
                    "pali": "",
                    "english": "",
                    "sinhala": "",
                    "paliTitle": pending_pali_title if pending_pali_title else ""
                }
                current_lines = [rest_of_line]
                pending_pali_title = None  # Reset after using
            
            # Regular content line
            else:
                if current_section is not None:
                    current_lines.append(line_stripped)
        
        # Save the last section
        if current_section is not None:
            current_section['pali'] = ' '.join(current_lines)
            sections.append(current_section)
        
        return sections
    
    def create_chapter_json(self, chapter_info: Dict, chapter_text: str, chapter_start_line: int) -> Dict:
        """
        Create a JSON structure for a chapter
        
        Args:
            chapter_info: Dictionary with chapter metadata
            chapter_text: The text content of the chapter
            chapter_start_line: Starting line number in full text
            
        Returns:
            Dictionary in the format of chapter_template.json
        """
        # Extract sections
        sections = self.extract_sections_from_chapter(chapter_text, chapter_start_line)
        
        # Get chapter title
        pali_title = chapter_info['title']
        
        chapter_json = {
            "id": chapter_info['id'],
            "title": {
                "pali": pali_title,
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
        """
        Save a chapter JSON to a file
        
        Args:
            chapter_info: Chapter metadata
            chapter_json: Chapter JSON structure
        """
        filename = f"{chapter_info['id']}-{chapter_info['title']}.json"
        output_path = os.path.join(self.output_dir, "chapters", filename)
        
        # Create chapters directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chapter_json, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved: {filename} ({len(chapter_json['sections'])} sections)")
    
    def create_book_json(self, chapters: List[Dict]):
        """
        Create a book.json file with metadata about all chapters
        
        Args:
            chapters: List of chapter metadata
        """
        book_json = {
            "name": self.book_config['name'],
            "title": {
                "pali": self.book_config['pali_title'],
                "english": self.book_config.get('english_title', ''),
                "sinhala": self.book_config.get('sinhala_title', '')
            },
            "chapters": [
                {
                    "id": ch['id'],
                    "title": {
                        "pali": ch['title'],
                        "english": "",
                        "sinhala": ""
                    }
                }
                for ch in chapters
            ]
        }
        
        output_path = os.path.join(self.output_dir, "book.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(book_json, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Saved book metadata: book.json")
    
    def process(self):
        """
        Main processing method - extract PDF and create JSON files
        """
        print("=" * 70)
        print(f"{self.book_config['name']} PDF Extraction")
        print("=" * 70)
        
        # Step 1: Extract text from PDF
        print("\n[1/6] Extracting text from PDF...")
        self.full_text, self.full_text_with_formatting = self.extract_text_from_pdf()
        
        # Step 2: Clean the text
        print("\n[2/6] Cleaning text...")
        self.full_text = self.clean_text(self.full_text)
        
        # Step 3: Save full text
        print("\n[3/6] Saving full extracted text...")
        self.save_full_text(self.full_text)
        
        # Step 4: Auto-detect or use provided chapters
        print("\n[4/6] Identifying chapters...")
        if 'chapters' in self.book_config and self.book_config['chapters']:
            chapters = self.book_config['chapters']
            print(f"✓ Using {len(chapters)} pre-configured chapters")
        else:
            chapters = self.auto_detect_chapters(self.full_text)
        
        # Step 5: Find chapter boundaries
        print("\n[5/6] Finding chapter boundaries...")
        boundaries = self.find_chapter_boundaries(self.full_text, chapters)
        
        # Step 6: Process each chapter
        print("\n[6/6] Creating chapter JSON files...")
        lines = self.full_text.split('\n')
        
        for start_line, end_line, chapter_info in boundaries:
            chapter_lines = lines[start_line:end_line]
            chapter_text = '\n'.join(chapter_lines)
            
            print(f"\nProcessing {chapter_info['title']}...")
            print(f"  Lines: {start_line} to {end_line} ({len(chapter_lines)} lines)")
            
            # Create chapter JSON
            chapter_json = self.create_chapter_json(chapter_info, chapter_text, start_line)
            
            # Save chapter JSON
            self.save_chapter_json(chapter_info, chapter_json)
        
        # Create book.json
        self.create_book_json(chapters)
        
        print("\n" + "=" * 70)
        print("✅ Extraction Complete!")
        print("=" * 70)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Full text: {os.path.join(self.output_dir, self.book_config['name'] + '_pali_extracted.txt')}")
        print(f"Chapter JSONs: {os.path.join(self.output_dir, 'chapters')}")
        print(f"Book metadata: {os.path.join(self.output_dir, 'book.json')}")


def main():
    """Main entry point"""
    
    # Configuration for Sīlakkhandhavaggapāḷi
    book_config = {
        'name': 'Pāthikavaggapāḷi',
        'pali_title': 'Pāthikavaggapāḷi',
        'english_title': '',
        'sinhala_title': '',
        'starting_dn': 1,  # Starts with DN 1
        'chapters': [],  # Will auto-detect
        'renumber_sections': False  # Keep original continuous section numbering from PDF
    }
    
    pdf_path = "pdfs/Pāthikavaggapāḷi.pdf"
    output_dir = "Pāthikavaggapāḷi"
    
    # Verify PDF exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return
    
    # Create extractor and process
    extractor = PaliPDFExtractor(pdf_path, output_dir, book_config)
    extractor.process()


if __name__ == "__main__":
    main()

