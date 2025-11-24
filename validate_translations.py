#!/usr/bin/env python3
"""
Validation script to detect foreign characters in Sinhala translations.
Checks for Tamil, Bengali, Hindi, and other non-Sinhala Unicode characters.
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Unicode ranges for different scripts
SINHALA_RANGE = r'\u0D80-\u0DFF'
TAMIL_RANGE = r'\u0B80-\u0BFF'
BENGALI_RANGE = r'\u0980-\u09FF'
DEVANAGARI_RANGE = r'\u0900-\u097F'  # Hindi
TELUGU_RANGE = r'\u0C00-\u0C7F'
KANNADA_RANGE = r'\u0C80-\u0CFF'
MALAYALAM_RANGE = r'\u0D00-\u0D7F'

# Pattern to detect foreign characters (non-Sinhala Indic scripts)
FOREIGN_CHARS_PATTERN = re.compile(
    f'[{TAMIL_RANGE}{BENGALI_RANGE}{DEVANAGARI_RANGE}{TELUGU_RANGE}{KANNADA_RANGE}{MALAYALAM_RANGE}]'
)

# Pattern to identify the script
SCRIPT_PATTERNS = {
    'Tamil': re.compile(f'[{TAMIL_RANGE}]'),
    'Bengali': re.compile(f'[{BENGALI_RANGE}]'),
    'Hindi/Devanagari': re.compile(f'[{DEVANAGARI_RANGE}]'),
    'Telugu': re.compile(f'[{TELUGU_RANGE}]'),
    'Kannada': re.compile(f'[{KANNADA_RANGE}]'),
    'Malayalam': re.compile(f'[{MALAYALAM_RANGE}]'),
}


def identify_script(char: str) -> str:
    """Identify which script a character belongs to."""
    for script_name, pattern in SCRIPT_PATTERNS.items():
        if pattern.match(char):
            return script_name
    return "Unknown"


def extract_context(text: str, position: int, context_length: int = 30) -> str:
    """Extract context around a position in text."""
    start = max(0, position - context_length)
    end = min(len(text), position + context_length)
    context = text[start:end]
    
    # Add ellipsis if truncated
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."
    
    return context


def find_foreign_chars(text: str) -> List[Dict]:
    """Find all foreign characters in Sinhala text."""
    issues = []
    
    for match in FOREIGN_CHARS_PATTERN.finditer(text):
        char = match.group()
        position = match.start()
        script = identify_script(char)
        context = extract_context(text, position)
        
        # Highlight the problematic character
        highlight_pos = position - max(0, position - 30)
        if position > 30:
            highlight_pos += 3  # Account for "..."
        
        issues.append({
            'char': char,
            'unicode': f'U+{ord(char):04X}',
            'script': script,
            'position': position,
            'context': context,
            'highlight_pos': highlight_pos
        })
    
    return issues


def validate_json_file(file_path: Path) -> Tuple[bool, List[Dict]]:
    """Validate a single JSON file for foreign characters in Sinhala translations."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        all_issues = []
        
        # Check title
        if 'title' in data and 'sinhala' in data['title']:
            issues = find_foreign_chars(data['title']['sinhala'])
            if issues:
                for issue in issues:
                    issue['location'] = 'title.sinhala'
                    issue['section_number'] = None
                all_issues.extend(issues)
        
        # Check sections
        if 'sections' in data:
            for section in data['sections']:
                if 'sinhala' in section:
                    issues = find_foreign_chars(section['sinhala'])
                    if issues:
                        section_num = section.get('number', 'unknown')
                        for issue in issues:
                            issue['location'] = f'section {section_num}'
                            issue['section_number'] = section_num
                        all_issues.extend(issues)
        
        return len(all_issues) == 0, all_issues
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, []


def print_issue(issue: Dict, file_path: Path):
    """Print a single issue in a formatted way."""
    print(f"\n  Location: {issue['location']}")
    print(f"  Character: '{issue['char']}' ({issue['unicode']}) - {issue['script']} script")
    print(f"  Position: {issue['position']}")
    print(f"  Context: {issue['context']}")
    
    # Show pointer to the problematic character
    pointer = " " * (11 + issue['highlight_pos']) + "^"
    print(pointer)


def validate_directory(directory: Path, pattern: str = "*.json") -> Dict:
    """Validate all JSON files in a directory."""
    results = {
        'total_files': 0,
        'valid_files': 0,
        'invalid_files': 0,
        'total_issues': 0,
        'files_with_issues': []
    }
    
    json_files = list(directory.rglob(pattern))
    
    if not json_files:
        print(f"No JSON files found in {directory}")
        return results
    
    print(f"Validating {len(json_files)} JSON files in {directory}...\n")
    
    for file_path in json_files:
        results['total_files'] += 1
        is_valid, issues = validate_json_file(file_path)
        
        if is_valid:
            results['valid_files'] += 1
            print(f"✓ {file_path.name} - OK")
        else:
            results['invalid_files'] += 1
            results['total_issues'] += len(issues)
            results['files_with_issues'].append({
                'file': file_path,
                'issues': issues
            })
            print(f"✗ {file_path.name} - {len(issues)} issue(s) found")
            
            for issue in issues:
                print_issue(issue, file_path)
    
    return results


def print_summary(results: Dict):
    """Print validation summary."""
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"Total files checked: {results['total_files']}")
    print(f"Valid files: {results['valid_files']}")
    print(f"Files with issues: {results['invalid_files']}")
    print(f"Total issues found: {results['total_issues']}")
    
    if results['files_with_issues']:
        print("\nFiles requiring fixes:")
        for item in results['files_with_issues']:
            print(f"  - {item['file'].name} ({len(item['issues'])} issues)")


def main():
    """Main validation function."""
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])
    else:
        target_path = Path(".")
    
    if not target_path.exists():
        print(f"Error: Path '{target_path}' does not exist")
        sys.exit(1)
    
    if target_path.is_file():
        # Validate single file
        print(f"Validating {target_path}...\n")
        is_valid, issues = validate_json_file(target_path)
        
        if is_valid:
            print(f"✓ {target_path.name} - OK")
            sys.exit(0)
        else:
            print(f"✗ {target_path.name} - {len(issues)} issue(s) found")
            for issue in issues:
                print_issue(issue, target_path)
            sys.exit(1)
    else:
        # Validate directory
        results = validate_directory(target_path)
        print_summary(results)
        
        if results['invalid_files'] > 0:
            sys.exit(1)
        else:
            print("\n✓ All files are valid!")
            sys.exit(0)


if __name__ == "__main__":
    main()

