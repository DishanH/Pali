"""
Quick utility to check a specific JSON file for character issues
Shows detailed report of all problems found
"""

import json
import re
import sys
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# Unicode ranges for different scripts
TAMIL_RANGE = r'\u0B80-\u0BFF'
BENGALI_RANGE = r'\u0980-\u09FF'
DEVANAGARI_RANGE = r'\u0900-\u097F'
TELUGU_RANGE = r'\u0C00-\u0C7F'
KANNADA_RANGE = r'\u0C80-\u0CFF'
MALAYALAM_RANGE = r'\u0D00-\u0D7F'

FOREIGN_PATTERN = re.compile(
    f'[{TAMIL_RANGE}{BENGALI_RANGE}{DEVANAGARI_RANGE}{TELUGU_RANGE}{KANNADA_RANGE}{MALAYALAM_RANGE}]'
)

SCRIPT_PATTERNS = {
    'Tamil': re.compile(f'[{TAMIL_RANGE}]'),
    'Bengali': re.compile(f'[{BENGALI_RANGE}]'),
    'Hindi/Devanagari': re.compile(f'[{DEVANAGARI_RANGE}]'),
    'Telugu': re.compile(f'[{TELUGU_RANGE}]'),
    'Kannada': re.compile(f'[{KANNADA_RANGE}]'),
    'Malayalam': re.compile(f'[{MALAYALAM_RANGE}]'),
}


def check_text(text: str, location: str):
    """Check text for foreign characters and report"""
    issues = []
    
    for match in FOREIGN_PATTERN.finditer(text):
        char = match.group()
        position = match.start()
        
        script = "Unknown"
        for script_name, pattern in SCRIPT_PATTERNS.items():
            if pattern.match(char):
                script = script_name
                break
        
        # Get context (30 chars before and after)
        start = max(0, position - 30)
        end = min(len(text), position + 30)
        context = text[start:end]
        
        # Highlight the problematic character
        relative_pos = position - start
        highlighted = (
            context[:relative_pos] + 
            f"[{char}]" + 
            context[relative_pos + 1:]
        )
        
        issues.append({
            'char': char,
            'unicode': f'U+{ord(char):04X}',
            'script': script,
            'position': position,
            'context': highlighted
        })
    
    if issues:
        print(f"\n  ❌ {location}")
        print(f"     Found {len(issues)} foreign character(s):")
        
        for i, issue in enumerate(issues, 1):
            print(f"\n     Issue {i}:")
            print(f"       Character: '{issue['char']}'")
            print(f"       Unicode: {issue['unicode']}")
            print(f"       Script: {issue['script']}")
            print(f"       Position: {issue['position']}")
            print(f"       Context: ...{issue['context']}...")
    else:
        print(f"  ✓ {location} - OK")
    
    return len(issues)


def check_json_file(file_path: str):
    """Check a JSON file for character issues"""
    print(f"\n{'='*70}")
    print(f"Checking: {file_path}")
    print(f"{'='*70}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not read file: {e}")
        return
    
    total_issues = 0
    
    # Check title
    print("\n📖 Checking Title:")
    if 'title' in data:
        if 'english' in data['title']:
            english_title = data['title']['english']
            if english_title:
                print(f"  English: {english_title}")
        
        if 'sinhala' in data['title']:
            sinhala_title = data['title']['sinhala']
            if sinhala_title:
                print(f"  Sinhala: {sinhala_title}")
                total_issues += check_text(sinhala_title, "Title (Sinhala)")
    
    # Check sections
    print("\n📄 Checking Sections:")
    sections = data.get('sections', [])
    print(f"  Total sections: {len(sections)}")
    
    sections_with_issues = []
    
    for i, section in enumerate(sections):
        section_num = section.get('number', i+1)
        
        # Check Sinhala translation
        if 'sinhala' in section and section['sinhala']:
            issues_count = check_text(
                section['sinhala'], 
                f"Section {i+1} (number: {section_num})"
            )
            
            if issues_count > 0:
                sections_with_issues.append({
                    'index': i,
                    'number': section_num,
                    'issues': issues_count
                })
                total_issues += issues_count
        
        # Also check English for completeness
        if 'english' in section and section['english']:
            # Check for truncation
            english_text = section['english']
            if english_text.endswith('...') or len(english_text) < 50:
                print(f"\n  ⚠ Section {i+1} (number: {section_num})")
                print(f"     English translation may be incomplete: {len(english_text)} chars")
    
    # Summary
    print(f"\n{'='*70}")
    print("Summary:")
    print(f"{'='*70}")
    print(f"Total sections: {len(sections)}")
    print(f"Sections with character issues: {len(sections_with_issues)}")
    print(f"Total foreign characters found: {total_issues}")
    
    if sections_with_issues:
        print(f"\n⚠ Sections that need fixing:")
        for sec in sections_with_issues:
            print(f"  - Section {sec['index']+1} (number: {sec['number']}): {sec['issues']} issue(s)")
        
        print(f"\n💡 To fix these issues, run:")
        print(f"   python fix_invalid_characters.py")
    else:
        print(f"\n✅ No character issues found!")
    
    print(f"\n{'='*70}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_file_issues.py <path_to_json_file>")
        print("\nExample:")
        print("  python check_file_issues.py Mahāvaggapāḷi/chapters/dn21-Sakkapañhasuttaṃ.json")
        
        # If no argument, ask for input
        file_path = input("\nEnter path to JSON file: ").strip()
        if not file_path:
            return
    else:
        file_path = sys.argv[1]
    
    check_json_file(file_path)


if __name__ == "__main__":
    main()

