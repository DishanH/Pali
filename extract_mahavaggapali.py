"""
PDF Extraction Script for Mahāvaggapāḷi
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

class MahavaggaPaliExtractor:
    """Extract Pali text from Mahāvaggapāḷi PDF and create chapter JSON files"""
    
    def __init__(self, pdf_path: str, output_dir: str):
        """
        Initialize the extractor
        
        Args:
            pdf_path: Path to the Mahāvaggapāḷi PDF file
            output_dir: Directory to save the extracted JSON files
        """
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.full_text = ""
        
        # Patterns to remove (metadata)
        self.remove_patterns = [
            r'Page \d+ sur \d+',  # Page numbers like "Page 1 sur 144"
            r'www\.tipitaka\.org',  # Website URL
            r'Vipassana.*Research Institute',  # Organization (with any content between)
            r'^\s*\d+\s*$',  # Lines with only numbers
        ]
        
        # Chapter information for Mahāvaggapāḷi
        self.chapters = [
            {"id": "dn14", "number": 14, "title": "Mahāpadānasuttaṃ"},
            {"id": "dn15", "number": 15, "title": "Mahānidānasuttaṃ"},
            {"id": "dn16", "number": 16, "title": "Mahāparinibbānasuttaṃ"},
        ]
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_text_from_pdf(self) -> str:
        """
        Extract text from PDF with proper character handling to avoid spaces in words
        
        Returns:
            Extracted text as a string
        """
        print(f"Opening PDF: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        
        all_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text with layout preservation
            # Using "text" mode which is better for continuous text
            text = page.get_text("text")
            
            if text.strip():
                all_text.append(text)
            
            if (page_num + 1) % 10 == 0:
                print(f"  Processed {page_num + 1}/{len(doc)} pages...")
        
        print(f"✓ Extracted text from {len(doc)} pages")
        doc.close()
        
        return '\n'.join(all_text)
    
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
            
            # Skip empty lines initially, we'll add them back strategically
            if not line:
                continue
            
            # Remove metadata patterns from within the line
            for pattern in self.remove_patterns:
                line = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
            
            # Check if line should be completely removed (now empty or still contains metadata)
            should_remove = False
            if not line:  # Line became empty after cleaning
                should_remove = True
            
            if not should_remove:
                cleaned_lines.append(line)
        
        # Join with single newline (no need for \n characters in output)
        cleaned_text = '\n'.join(cleaned_lines)
        
        print(f"✓ Cleaned text: {len(cleaned_lines)} lines")
        return cleaned_text
    
    def save_full_text(self, text: str, filename: str = "Mahāvaggapāḷi_pali_extracted.txt"):
        """
        Save the full extracted text to a file
        
        Args:
            text: The text to save
            filename: Output filename
        """
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✓ Saved full text to: {output_path}")
    
    def find_chapter_boundaries(self, text: str) -> List[Tuple[int, int, Dict]]:
        """
        Find the start and end positions of each chapter in the text
        
        Args:
            text: The full cleaned text
            
        Returns:
            List of tuples: (start_pos, end_pos, chapter_info)
        """
        print("\nFinding chapter boundaries...")
        
        lines = text.split('\n')
        boundaries = []
        
        for i, chapter_info in enumerate(self.chapters):
            chapter_title = chapter_info['title']
            
            # Find chapter start
            start_line = None
            for line_num, line in enumerate(lines):
                # Look for pattern like "1. Mahāpadānasuttaṃ" or just "Mahāpadānasuttaṃ"
                if re.search(r'\d+\.\s+' + re.escape(chapter_title), line) or \
                   (line.strip() == chapter_title and len(line.strip()) < 100):
                    start_line = line_num
                    print(f"  ✓ Found chapter {chapter_info['number']}: {chapter_title} at line {line_num}")
                    break
            
            if start_line is None:
                print(f"  ✗ Warning: Could not find chapter: {chapter_title}")
                continue
            
            # Find chapter end (start of next chapter or end of file)
            end_line = len(lines)
            if i + 1 < len(self.chapters):
                next_chapter_title = self.chapters[i + 1]['title']
                for line_num in range(start_line + 1, len(lines)):
                    line = lines[line_num]
                    if re.search(r'\d+\.\s+' + re.escape(next_chapter_title), line) or \
                       (line.strip() == next_chapter_title and len(line.strip()) < 100):
                        end_line = line_num
                        break
            
            boundaries.append((start_line, end_line, chapter_info))
        
        return boundaries
    
    def detect_section_title(self, line: str) -> Optional[str]:
        """
        Detect if a line is a section title (paliTitle)
        
        Section titles are typically:
        - Short lines (< 100 chars)
        - End with certain patterns (vatthu, kathā, vaṇṇanā, dhammā, etc.)
        - Are capitalized or follow specific patterns
        - Do NOT start with quotes or contain long sentences
        
        Args:
            line: The line to check
            
        Returns:
            The title if detected, None otherwise
        """
        line = line.strip()
        
        # Skip if too long, empty, or starts with quotes (not a title)
        if len(line) > 100 or len(line) == 0 or line.startswith("'") or line.startswith('"'):
            return None
        
        # Skip if it contains sentence-like structures (commas, semicolons, etc.)
        if ',' in line or ';' in line or '?' in line:
            return None
        
        # Check for common section title endings
        title_patterns = [
            r'vatthu$',
            r'kathā$',
            r'vaṇṇanā$',
            r'dhammā$',
            r'dhammatā$',
            r'lakkhaṇā$',
            r'lakkhaṇaṃ$',
            r'paṭisaṃyutta',
            r'nidāna',
            r'vagga$',
        ]
        
        for pattern in title_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return line
        
        return None
    
    def extract_sections_from_chapter(self, chapter_text: str) -> List[Dict]:
        """
        Extract sections from a chapter text
        
        Each section is identified by a number pattern like "1. ", "2. ", etc.
        
        Args:
            chapter_text: The text of a single chapter
            
        Returns:
            List of section dictionaries
        """
        lines = chapter_text.split('\n')
        sections = []
        current_section = None
        current_lines = []
        pending_pali_title = None
        
        # Skip the first line if it's the chapter title
        start_idx = 0
        if lines and re.match(r'^\d+\.\s+\w+suttaṃ', lines[0].strip()):
            start_idx = 1
        
        for i in range(start_idx, len(lines)):
            line_stripped = lines[i].strip()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Check if this is a section title (should come before numbered sections)
            detected_title = self.detect_section_title(line_stripped)
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
                
                # Start new section
                section_num = int(section_match.group(1))
                rest_of_line = section_match.group(2)
                
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
    
    def create_chapter_json(self, chapter_info: Dict, chapter_text: str) -> Dict:
        """
        Create a JSON structure for a chapter
        
        Args:
            chapter_info: Dictionary with chapter metadata
            chapter_text: The text content of the chapter
            
        Returns:
            Dictionary in the format of chapter_template.json
        """
        # Extract sections
        sections = self.extract_sections_from_chapter(chapter_text)
        
        # Get chapter title from the first line if available
        first_line = chapter_text.split('\n')[0].strip()
        chapter_title_match = re.match(r'^\d+\.\s+(.+)', first_line)
        if chapter_title_match:
            pali_title = chapter_title_match.group(1)
        else:
            pali_title = chapter_info['title']
        
        chapter_json = {
            "id": chapter_info['id'],
            "title": {
                "pali": pali_title,
                "english": "",
                "sinhala": ""
            },
            "sections": sections
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
    
    def process(self):
        """
        Main processing method - extract PDF and create JSON files
        """
        print("=" * 70)
        print("Mahāvaggapāḷi PDF Extraction")
        print("=" * 70)
        
        # Step 1: Extract text from PDF
        print("\n[1/5] Extracting text from PDF...")
        self.full_text = self.extract_text_from_pdf()
        
        # Step 2: Clean the text
        print("\n[2/5] Cleaning text...")
        self.full_text = self.clean_text(self.full_text)
        
        # Step 3: Save full text
        print("\n[3/5] Saving full extracted text...")
        self.save_full_text(self.full_text)
        
        # Step 4: Find chapter boundaries
        print("\n[4/5] Identifying chapters...")
        boundaries = self.find_chapter_boundaries(self.full_text)
        
        # Step 5: Process each chapter
        print("\n[5/5] Creating chapter JSON files...")
        lines = self.full_text.split('\n')
        
        for start_line, end_line, chapter_info in boundaries:
            chapter_lines = lines[start_line:end_line]
            chapter_text = '\n'.join(chapter_lines)
            
            print(f"\nProcessing {chapter_info['title']}...")
            print(f"  Lines: {start_line} to {end_line} ({len(chapter_lines)} lines)")
            
            # Create chapter JSON
            chapter_json = self.create_chapter_json(chapter_info, chapter_text)
            
            # Save chapter JSON
            self.save_chapter_json(chapter_info, chapter_json)
        
        print("\n" + "=" * 70)
        print("✅ Extraction Complete!")
        print("=" * 70)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Full text: {os.path.join(self.output_dir, 'Mahāvaggapāḷi_pali_extracted.txt')}")
        print(f"Chapter JSONs: {os.path.join(self.output_dir, 'chapters')}")


def main():
    """Main entry point"""
    # Configuration
    pdf_path = "pdfs/Mahāvaggapāḷi.pdf"
    output_dir = "Mahāvaggapāḷi"
    
    # Verify PDF exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return
    
    # Create extractor and process
    extractor = MahavaggaPaliExtractor(pdf_path, output_dir)
    extractor.process()


if __name__ == "__main__":
    main()

