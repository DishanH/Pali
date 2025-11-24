"""
Test script to verify section extraction from Pali text
"""

import sys
import os
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def extract_chapter_from_text(text: str, chapter_marker: str, next_chapter_marker: str = None) -> str:
    """Extract a specific chapter from the full text"""
    lines = text.split('\n')
    
    start_idx = None
    end_idx = None
    
    # Find the FIRST occurrence with chapter number pattern
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        if start_idx is None:
            # Match chapter number followed by the marker
            if re.match(r'^\d+\.\s+' + re.escape(chapter_marker), line_stripped):
                start_idx = i
                print(f"✓ Found chapter start at line {i}: {line_stripped[:60]}")
        elif next_chapter_marker:
            # Look for next chapter pattern
            if re.match(r'^\d+\.\s+' + re.escape(next_chapter_marker), line_stripped):
                end_idx = i
                print(f"✓ Found chapter end at line {i}: {line_stripped[:60]}")
                break
    
    if start_idx is None:
        print(f"✗ Could not find chapter marker: {chapter_marker}")
        return ""
    
    if end_idx is None:
        chapter_lines = lines[start_idx:]
        print(f"✓ Extracting from line {start_idx} to end of file ({len(chapter_lines)} lines)")
    else:
        chapter_lines = lines[start_idx:end_idx]
        print(f"✓ Extracting from line {start_idx} to {end_idx} ({len(chapter_lines)} lines)")
    
    return '\n'.join(chapter_lines)


def count_numbered_sections(text: str) -> int:
    """Count how many numbered sections (1., 2., 3., etc.) are in the text"""
    lines = text.split('\n')
    numbered_sections = set()
    
    for line in lines:
        line_stripped = line.strip()
        numbered_match = re.match(r'^(\d+)\s*\.\s+(.+)', line_stripped)
        
        if numbered_match:
            section_number = numbered_match.group(1)
            content = numbered_match.group(2)
            
            # Exclude main chapter titles
            is_chapter_title = content.endswith('suttaṃ') or content.endswith('suttantaṃ')
            
            if not is_chapter_title:
                numbered_sections.add(int(section_number))
    
    return len(numbered_sections), sorted(numbered_sections)


def find_sub_headings(text: str) -> list:
    """Find all sub-headings (vatthu, kathā, etc.)"""
    lines = text.split('\n')
    sub_headings = []
    
    for line in lines:
        line_stripped = line.strip()
        if (len(line_stripped) < 100 and 
            (line_stripped.endswith('vatthu') or 
             line_stripped.endswith('kathā') or
             line_stripped.endswith('vaṇṇanā'))):
            sub_headings.append(line_stripped)
    
    return sub_headings


def main():
    print("=" * 60)
    print("Section Extraction Test")
    print("=" * 60)
    
    # Read the Pali text
    pali_file = os.path.join("Pāthikavaggapāḷi", "Pāthikavaggapāḷi_pali_extracted.txt")
    
    try:
        with open(pali_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
        print(f"\n✓ Loaded Pali text: {len(full_text)} characters")
    except Exception as e:
        print(f"\n✗ Failed to read Pali text: {e}")
        return
    
    # Test extracting Chapter 1 (Pāthikasuttaṃ)
    print("\n" + "-" * 60)
    print("Extracting Chapter 1: Pāthikasuttaṃ")
    print("-" * 60)
    
    chapter_text = extract_chapter_from_text(
        full_text,
        "Pāthikasuttaṃ",
        "Udumbarikasuttaṃ"  # Next chapter
    )
    
    if chapter_text:
        print(f"\n✓ Successfully extracted chapter")
        print(f"  Chapter length: {len(chapter_text)} characters")
        
        # Count numbered sections
        num_sections, section_numbers = count_numbered_sections(chapter_text)
        print(f"\n✓ Found {num_sections} numbered sections")
        
        if num_sections > 0:
            print(f"  Section numbers: {', '.join(map(str, section_numbers[:10]))}{'...' if num_sections > 10 else ''}")
            
            # Show range
            if num_sections > 1:
                print(f"  Range: {min(section_numbers)} to {max(section_numbers)}")
        
        # Find sub-headings
        sub_headings = find_sub_headings(chapter_text)
        print(f"\n✓ Found {len(sub_headings)} sub-headings (vatthu/kathā)")
        for heading in sub_headings[:5]:
            print(f"  - {heading}")
        if len(sub_headings) > 5:
            print(f"  ... and {len(sub_headings) - 5} more")
        
        # Show first few lines
        print("\n" + "-" * 60)
        print("First 20 lines of extracted chapter:")
        print("-" * 60)
        lines = chapter_text.split('\n')
        for i, line in enumerate(lines[:20], 1):
            print(f"{i:3d}: {line[:70]}")
        
        # Expected result
        print("\n" + "=" * 60)
        print("VALIDATION")
        print("=" * 60)
        
        expected_sections = 48  # Based on your observation
        
        if num_sections == expected_sections:
            print(f"✅ SUCCESS: Found exactly {expected_sections} sections!")
        elif num_sections > 0:
            print(f"⚠️  PARTIAL: Found {num_sections} sections (expected ~{expected_sections})")
            print(f"   This might be correct depending on how sections are counted.")
        else:
            print(f"✗ FAILED: Found {num_sections} sections (expected {expected_sections})")
            print(f"  The extraction may not be working correctly.")
    else:
        print("\n✗ Failed to extract chapter")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

