#!/usr/bin/env python3
"""
Generate a manual fix guide for foreign characters in Sinhala translations.
This script identifies issues and suggests corrections based on context.
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict

# Unicode ranges
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

# Common mappings for automatic fixes
COMMON_FIXES = {
    # Tamil characters that commonly appear instead of Sinhala
    'ம': 'ම',  # ma
    'ா': 'ා',  # aa
    'ன': 'න',  # na
    'ு': 'ු',  # u
    'ர': 'ර',  # ra
    'ீ': 'ී',  # ii
    
    # Bengali characters
    'উ': 'උ',  # u
    'প': 'ප',  # pa
    'ব': 'බ',  # ba
    'ি': 'ි',  # i
    'ষ': 'ෂ',  # sha
    '্': '්',  # virama
    'ট': 'ට',  # ta
    
    # Telugu characters
    'ఇ': 'ඉ',  # i
    'క': 'ක',  # ka
    'ప': 'ප',  # pa
    'ై': 'ෛ',  # ai
    
    # Malayalam characters
    'ന': 'න',  # na
    '്': '්',  # virama
    'ി': 'ි',  # i
    'അ': 'අ',  # a
    'ത': 'ත',  # ta
    'ഹ': 'හ',  # ha
    'ഞ': 'ඤ',  # nya
}


def find_foreign_chars(text: str) -> List[Dict]:
    """Find all foreign characters in Sinhala text."""
    issues = []
    
    for match in FOREIGN_PATTERN.finditer(text):
        char = match.group()
        position = match.start()
        
        # Identify script
        script = "Unknown"
        for script_name, pattern in SCRIPT_PATTERNS.items():
            if pattern.match(char):
                script = script_name
                break
        
        # Extract context
        start = max(0, position - 40)
        end = min(len(text), position + 40)
        context = text[start:end]
        
        # Suggest fix
        suggested_fix = COMMON_FIXES.get(char, '?')
        
        issues.append({
            'char': char,
            'unicode': f'U+{ord(char):04X}',
            'script': script,
            'position': position,
            'context': context,
            'suggested_fix': suggested_fix
        })
    
    return issues


def auto_fix_text(text: str) -> tuple[str, int]:
    """Automatically fix text using common mappings."""
    fixed_text = text
    fixes_applied = 0
    
    for foreign_char, sinhala_char in COMMON_FIXES.items():
        if foreign_char in fixed_text:
            count = fixed_text.count(foreign_char)
            fixed_text = fixed_text.replace(foreign_char, sinhala_char)
            fixes_applied += count
    
    return fixed_text, fixes_applied


def generate_fix_guide(file_path: Path, auto_fix: bool = False):
    """Generate a fix guide for a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return
    
    print(f"\n{'='*80}")
    print(f"FIX GUIDE FOR: {file_path.name}")
    print(f"{'='*80}\n")
    
    total_issues = 0
    total_fixes = 0
    modified = False
    
    # Check title
    if 'title' in data and 'sinhala' in data['title']:
        issues = find_foreign_chars(data['title']['sinhala'])
        if issues:
            print(f"TITLE: {len(issues)} issue(s)")
            for issue in issues:
                print(f"  - {issue['script']} '{issue['char']}' → '{issue['suggested_fix']}'")
                print(f"    Context: ...{issue['context']}...")
            total_issues += len(issues)
            
            if auto_fix:
                fixed_text, fixes = auto_fix_text(data['title']['sinhala'])
                if fixes > 0:
                    data['title']['sinhala'] = fixed_text
                    total_fixes += fixes
                    modified = True
                    print(f"  ✓ Auto-fixed {fixes} character(s)")
            print()
    
    # Check sections
    if 'sections' in data:
        for section in data['sections']:
            if 'sinhala' in section:
                issues = find_foreign_chars(section['sinhala'])
                if issues:
                    section_num = section.get('number', '?')
                    print(f"SECTION {section_num}: {len(issues)} issue(s)")
                    
                    # Group issues by character for cleaner output
                    char_counts = {}
                    for issue in issues:
                        key = (issue['char'], issue['suggested_fix'], issue['script'])
                        char_counts[key] = char_counts.get(key, 0) + 1
                    
                    for (char, fix, script), count in char_counts.items():
                        print(f"  - {script} '{char}' → '{fix}' ({count} occurrence(s))")
                    
                    # Show first occurrence context
                    if issues:
                        print(f"    First context: ...{issues[0]['context']}...")
                    
                    total_issues += len(issues)
                    
                    if auto_fix:
                        fixed_text, fixes = auto_fix_text(section['sinhala'])
                        if fixes > 0:
                            section['sinhala'] = fixed_text
                            total_fixes += fixes
                            modified = True
                            print(f"  ✓ Auto-fixed {fixes} character(s)")
                    print()
    
    print(f"{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total foreign characters found: {total_issues}")
    
    if auto_fix:
        print(f"Total characters auto-fixed: {total_fixes}")
        
        if modified:
            # Save the fixed file
            backup_path = file_path.with_suffix('.json.bak')
            if not backup_path.exists():
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"\n✓ Created backup: {backup_path.name}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Saved fixed file: {file_path.name}")
            
            # Verify
            remaining_issues = 0
            if 'title' in data and 'sinhala' in data['title']:
                remaining_issues += len(find_foreign_chars(data['title']['sinhala']))
            if 'sections' in data:
                for section in data['sections']:
                    if 'sinhala' in section:
                        remaining_issues += len(find_foreign_chars(section['sinhala']))
            
            if remaining_issues > 0:
                print(f"\n⚠ Warning: {remaining_issues} foreign character(s) still remain")
                print("These may require manual review or AI assistance")
            else:
                print(f"\n✓ All foreign characters successfully fixed!")
    else:
        print("\nRun with --auto-fix flag to automatically apply common fixes")
    
    print()


def main():
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    if len(sys.argv) < 2:
        print("Usage: python manual_fix_guide.py <json_file> [--auto-fix]")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    auto_fix = '--auto-fix' in sys.argv
    
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist")
        sys.exit(1)
    
    generate_fix_guide(file_path, auto_fix)


if __name__ == "__main__":
    main()

