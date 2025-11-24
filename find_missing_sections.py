"""
Find Missing Sections in Chapter JSON Files
Identifies gaps in section numbering and extracts missing sections from PDF
"""

import json
import os
import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Tuple, Set


class MissingSectionFinder:
    """Find and extract missing sections from Mahāvaggapāḷi chapters"""
    
    def __init__(self, chapters_dir: str, pdf_path: str, output_file: str = "missing_sections.json"):
        """
        Initialize the finder
        
        Args:
            chapters_dir: Directory containing chapter JSON files
            pdf_path: Path to the source PDF
            output_file: Output file for missing sections
        """
        self.chapters_dir = chapters_dir
        self.pdf_path = pdf_path
        self.output_file = output_file
        self.missing_sections = {}
    
    def find_missing_numbers(self, sections: List[Dict]) -> Set[int]:
        """
        Find missing section numbers in a sequence
        
        Args:
            sections: List of section dictionaries
            
        Returns:
            Set of missing section numbers
        """
        if not sections:
            return set()
        
        # Get all section numbers
        section_numbers = [s.get('number', 0) for s in sections]
        section_numbers = [n for n in section_numbers if n > 0]
        
        if not section_numbers:
            return set()
        
        # Find min and max
        min_num = min(section_numbers)
        max_num = max(section_numbers)
        
        # Find missing numbers in the range
        expected = set(range(min_num, max_num + 1))
        actual = set(section_numbers)
        missing = expected - actual
        
        return missing
    
    def analyze_chapter(self, json_path: str) -> Dict:
        """
        Analyze a chapter JSON file for missing sections
        
        Args:
            json_path: Path to the chapter JSON file
            
        Returns:
            Dictionary with analysis results
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data.get('id', 'unknown')
        chapter_title = chapter_data.get('title', {}).get('pali', 'Unknown')
        sections = chapter_data.get('sections', [])
        
        # Find missing section numbers
        missing = self.find_missing_numbers(sections)
        
        # Get section number range
        section_numbers = [s.get('number', 0) for s in sections if s.get('number', 0) > 0]
        min_num = min(section_numbers) if section_numbers else 0
        max_num = max(section_numbers) if section_numbers else 0
        
        return {
            'file': os.path.basename(json_path),
            'chapter_id': chapter_id,
            'chapter_title': chapter_title,
            'total_sections': len(sections),
            'section_range': f"{min_num}-{max_num}",
            'missing_numbers': sorted(list(missing)),
            'has_missing': len(missing) > 0
        }
    
    def extract_text_from_pdf(self) -> str:
        """Extract full text from PDF"""
        print(f"Extracting text from PDF: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        
        all_text = []
        total_pages = len(doc)
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                all_text.append(text)
        
        doc.close()
        print(f"✓ Extracted text from {total_pages} pages")
        
        return '\n'.join(all_text)
    
    def find_section_in_text(self, full_text: str, chapter_title: str, section_num: int) -> Dict:
        """
        Find a specific section in the full text
        
        Args:
            full_text: The full PDF text
            chapter_title: Title of the chapter
            section_num: Section number to find
            
        Returns:
            Dictionary with section information
        """
        lines = full_text.split('\n')
        
        # First, find the chapter
        chapter_start = None
        for i, line in enumerate(lines):
            if chapter_title in line:
                chapter_start = i
                break
        
        if chapter_start is None:
            return {
                'section_number': section_num,
                'found': False,
                'error': f'Chapter "{chapter_title}" not found in PDF'
            }
        
        # Now find the section within the chapter
        section_pattern = re.compile(rf'^\s*{section_num}\.\s+(.+)')
        next_section_pattern = re.compile(rf'^\s*{section_num + 1}\.\s+')
        
        section_start = None
        section_end = None
        
        # Search from chapter start onwards
        for i in range(chapter_start, len(lines)):
            line = lines[i].strip()
            
            # Found the section start
            if section_start is None and section_pattern.match(line):
                section_start = i
                continue
            
            # Found the next section (end of current section)
            if section_start is not None and next_section_pattern.match(line):
                section_end = i
                break
        
        if section_start is None:
            return {
                'section_number': section_num,
                'found': False,
                'error': f'Section {section_num} not found in chapter'
            }
        
        # If no end found, search for any next numbered section
        if section_end is None:
            any_section_pattern = re.compile(r'^\s*(\d+)\.\s+')
            for i in range(section_start + 1, min(section_start + 200, len(lines))):
                line = lines[i].strip()
                match = any_section_pattern.match(line)
                if match and int(match.group(1)) > section_num:
                    section_end = i
                    break
        
        # Extract section text
        if section_end is None:
            section_end = min(section_start + 100, len(lines))  # Default to 100 lines
        
        section_lines = lines[section_start:section_end]
        
        # Clean and join
        cleaned_lines = []
        for line in section_lines:
            line = line.strip()
            # Remove metadata
            if re.match(r'Page \d+ sur \d+', line):
                continue
            if 'www.tipitaka.org' in line:
                continue
            if line:
                cleaned_lines.append(line)
        
        # Extract pali title if present (line before section number)
        pali_title = ""
        if section_start > 0:
            prev_line = lines[section_start - 1].strip()
            if len(prev_line) < 100 and not re.match(r'^\d+\.', prev_line):
                # Check if it looks like a title
                if any(prev_line.endswith(suffix) for suffix in ['vatthu', 'kathā', 'vaṇṇanā', 'dhammā']):
                    pali_title = prev_line
        
        # Remove section number from first line
        first_line = cleaned_lines[0] if cleaned_lines else ""
        first_line = re.sub(rf'^\s*{section_num}\.\s+', '', first_line)
        if cleaned_lines:
            cleaned_lines[0] = first_line
        
        section_text = ' '.join(cleaned_lines)
        
        return {
            'section_number': section_num,
            'found': True,
            'pali': section_text,
            'paliTitle': pali_title,
            'english': '',
            'sinhala': '',
            'line_range': f'{section_start}-{section_end}',
            'preview': section_text[:200] + '...' if len(section_text) > 200 else section_text
        }
    
    def process(self):
        """Main processing method"""
        print("=" * 70)
        print("Missing Section Finder for Mahāvaggapāḷi")
        print("=" * 70)
        
        # Step 1: Analyze all chapter JSON files
        print("\n[1/3] Analyzing chapter JSON files...")
        
        json_files = sorted(Path(self.chapters_dir).glob("*.json"))
        all_analyses = []
        
        for json_file in json_files:
            analysis = self.analyze_chapter(str(json_file))
            all_analyses.append(analysis)
            
            status = "❌ HAS MISSING" if analysis['has_missing'] else "✓ Complete"
            print(f"  {status} | {analysis['file']}")
            print(f"    Chapter: {analysis['chapter_title']}")
            print(f"    Sections: {analysis['total_sections']} (range: {analysis['section_range']})")
            
            if analysis['has_missing']:
                print(f"    Missing: {analysis['missing_numbers']}")
        
        # Count chapters with missing sections
        chapters_with_missing = [a for a in all_analyses if a['has_missing']]
        
        print(f"\n📊 Summary:")
        print(f"  Total chapters: {len(all_analyses)}")
        print(f"  Complete: {len(all_analyses) - len(chapters_with_missing)}")
        print(f"  With missing sections: {len(chapters_with_missing)}")
        
        if not chapters_with_missing:
            print("\n✅ All chapters are complete! No missing sections found.")
            return
        
        # Step 2: Extract missing sections from PDF
        print(f"\n[2/3] Extracting missing sections from PDF...")
        
        if not os.path.exists(self.pdf_path):
            print(f"❌ Error: PDF file not found: {self.pdf_path}")
            print("Cannot extract missing sections without PDF.")
            return
        
        full_text = self.extract_text_from_pdf()
        
        missing_sections_data = {}
        
        for analysis in chapters_with_missing:
            chapter_id = analysis['chapter_id']
            chapter_title = analysis['chapter_title']
            missing_nums = analysis['missing_numbers']
            
            print(f"\n  Processing {chapter_id}: {chapter_title}")
            print(f"    Missing sections: {missing_nums}")
            
            chapter_missing = []
            
            for section_num in missing_nums:
                print(f"    → Extracting section {section_num}...", end='')
                
                section_data = self.find_section_in_text(full_text, chapter_title, section_num)
                
                if section_data['found']:
                    print(f" ✓")
                    print(f"      Preview: {section_data['preview']}")
                    chapter_missing.append(section_data)
                else:
                    print(f" ✗")
                    print(f"      Error: {section_data.get('error', 'Unknown error')}")
                    chapter_missing.append(section_data)
            
            missing_sections_data[chapter_id] = {
                'chapter_title': chapter_title,
                'file': analysis['file'],
                'missing_sections': chapter_missing
            }
        
        # Step 3: Save results
        print(f"\n[3/3] Saving results...")
        
        output_data = {
            'summary': {
                'total_chapters_analyzed': len(all_analyses),
                'chapters_with_missing': len(chapters_with_missing),
                'total_missing_sections': sum(len(a['missing_numbers']) for a in chapters_with_missing)
            },
            'chapters': missing_sections_data
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Saved missing sections to: {self.output_file}")
        
        print("\n" + "=" * 70)
        print("✅ Analysis Complete!")
        print("=" * 70)
        print(f"\nResults saved to: {self.output_file}")
        print("\nNext steps:")
        print("1. Review the missing_sections.json file")
        print("2. Manually verify and correct the extracted sections")
        print("3. Insert them into the appropriate chapter JSON files")


def main():
    """Main entry point"""
    # Configuration
    chapters_dir = "Mahāvaggapāḷi/chapters"
    pdf_path = "pdfs/Mahāvaggapāḷi.pdf"
    output_file = "missing_sections.json"
    
    # Verify chapters directory exists
    if not os.path.exists(chapters_dir):
        print(f"❌ Error: Chapters directory not found: {chapters_dir}")
        return
    
    # Create finder and process
    finder = MissingSectionFinder(chapters_dir, pdf_path, output_file)
    finder.process()


if __name__ == "__main__":
    main()
