"""
Utility script to fix invalid foreign characters in existing JSON files
Scans Sinhala translations and fixes Tamil/Hindi/Telugu/etc. characters
"""

import json
import os
import re
import sys
import io
from pathlib import Path
import google.generativeai as genai

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Unicode ranges for different scripts
TAMIL_RANGE = r'\u0B80-\u0BFF'
BENGALI_RANGE = r'\u0980-\u09FF'
DEVANAGARI_RANGE = r'\u0900-\u097F'  # Hindi
TELUGU_RANGE = r'\u0C00-\u0C7F'
KANNADA_RANGE = r'\u0C80-\u0CFF'
MALAYALAM_RANGE = r'\u0D00-\u0D7F'

# Pattern to detect foreign characters
FOREIGN_PATTERN = re.compile(
    f'[{TAMIL_RANGE}{BENGALI_RANGE}{DEVANAGARI_RANGE}{TELUGU_RANGE}{KANNADA_RANGE}{MALAYALAM_RANGE}]'
)


def validate_sinhala_text(text: str) -> tuple:
    """
    Validate Sinhala text for foreign characters
    Returns: (is_valid, list_of_issues)
    """
    issues = []
    
    script_patterns = {
        'Tamil': re.compile(f'[{TAMIL_RANGE}]'),
        'Bengali': re.compile(f'[{BENGALI_RANGE}]'),
        'Hindi/Devanagari': re.compile(f'[{DEVANAGARI_RANGE}]'),
        'Telugu': re.compile(f'[{TELUGU_RANGE}]'),
        'Kannada': re.compile(f'[{KANNADA_RANGE}]'),
        'Malayalam': re.compile(f'[{MALAYALAM_RANGE}]'),
    }
    
    for match in FOREIGN_PATTERN.finditer(text):
        char = match.group()
        position = match.start()
        
        script = "Unknown"
        for script_name, pattern in script_patterns.items():
            if pattern.match(char):
                script = script_name
                break
        
        start = max(0, position - 30)
        end = min(len(text), position + 30)
        context = text[start:end]
        
        issues.append({
            'char': char,
            'unicode': f'U+{ord(char):04X}',
            'script': script,
            'position': position,
            'context': context
        })
    
    return len(issues) == 0, issues


def fix_text_with_ai(text: str, issues: list, api_key: str) -> str:
    """Use AI to fix the text by replacing foreign characters"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""The following Sinhala text contains FOREIGN script characters from other Indian languages.
Please rewrite it using ONLY proper Sinhala Unicode characters (U+0D80-U+0DFF).

Replace all foreign characters with proper Sinhala equivalents. Maintain the exact meaning.

PROBLEMATIC TEXT:
{text}

ISSUES FOUND:
{chr(10).join([f"- {issue['script']} character '{issue['char']}' ({issue['unicode']}) in context: ...{issue['context']}..." for issue in issues[:10]])}

Return ONLY the corrected Sinhala text (using ONLY Sinhala Unicode U+0D80-U+0DFF):"""
    
    try:
        response = model.generate_content(prompt)
        fixed_text = response.text.strip()
        return fixed_text
    except Exception as e:
        print(f"    ERROR: AI fix failed: {e}")
        return text


def scan_json_file(file_path: str) -> dict:
    """Scan a JSON file for invalid characters"""
    print(f"\n📄 Scanning: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    issues_found = []
    
    # Check title
    if 'title' in data and 'sinhala' in data['title']:
        sinhala_title = data['title']['sinhala']
        is_valid, issues = validate_sinhala_text(sinhala_title)
        if not is_valid:
            issues_found.append({
                'location': 'title',
                'text': sinhala_title,
                'issues': issues
            })
    
    # Check sections
    for i, section in enumerate(data.get('sections', [])):
        if 'sinhala' in section:
            sinhala_text = section['sinhala']
            is_valid, issues = validate_sinhala_text(sinhala_text)
            if not is_valid:
                issues_found.append({
                    'location': f'section[{i}] (number: {section.get("number", "?")})',
                    'text': sinhala_text,
                    'issues': issues
                })
    
    return {
        'file': file_path,
        'data': data,
        'issues_found': issues_found
    }


def fix_json_file(scan_result: dict, api_key: str, dry_run: bool = False) -> bool:
    """Fix invalid characters in a JSON file"""
    file_path = scan_result['file']
    data = scan_result['data']
    issues_found = scan_result['issues_found']
    
    if not issues_found:
        print(f"  ✓ No issues found")
        return False
    
    print(f"  ⚠ Found {len(issues_found)} location(s) with invalid characters")
    
    fixed_count = 0
    
    for issue_info in issues_found:
        location = issue_info['location']
        text = issue_info['text']
        issues = issue_info['issues']
        
        print(f"\n  🔧 Fixing {location}:")
        print(f"     Issues: {len(issues)} foreign characters")
        for issue in issues[:3]:
            print(f"       - {issue['script']}: '{issue['char']}' ({issue['unicode']})")
        
        if dry_run:
            print(f"     [DRY RUN] Would fix this text")
            continue
        
        # Fix the text
        print(f"     Calling AI to fix text...")
        fixed_text = fix_text_with_ai(text, issues, api_key)
        
        # Validate fix
        is_valid_now, remaining_issues = validate_sinhala_text(fixed_text)
        
        if is_valid_now:
            print(f"     ✓ Successfully fixed all foreign characters")
            
            # Update the data
            if location == 'title':
                data['title']['sinhala'] = fixed_text
            elif location.startswith('section['):
                section_idx = int(location.split('[')[1].split(']')[0])
                data['sections'][section_idx]['sinhala'] = fixed_text
            
            fixed_count += 1
        else:
            print(f"     ⚠ Still {len(remaining_issues)} foreign characters remain")
            print(f"     Using improved text anyway (likely better than original)")
            
            # Update the data with improved text
            if location == 'title':
                data['title']['sinhala'] = fixed_text
            elif location.startswith('section['):
                section_idx = int(location.split('[')[1].split(']')[0])
                data['sections'][section_idx]['sinhala'] = fixed_text
            
            fixed_count += 1
    
    if not dry_run and fixed_count > 0:
        # Save the fixed file
        backup_path = file_path + '.backup'
        
        # Create backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(scan_result['data'], f, ensure_ascii=False, indent=2)
        
        # Save fixed version
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n  ✅ Fixed {fixed_count} location(s)")
        print(f"  💾 Backup saved to: {backup_path}")
        return True
    
    return False


def main():
    print("=" * 70)
    print("Sinhala Character Validator and Fixer for JSON Files")
    print("=" * 70)
    
    # Get API key
    api_key = input("\nEnter your Google AI API key (or press Enter to use GOOGLE_API_KEY env var): ").strip()
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY", "")
    
    if not api_key:
        print("ERROR: No API key provided")
        return
    
    # Get file or directory path
    path_input = input("\nEnter path to JSON file or directory to scan: ").strip()
    
    if not os.path.exists(path_input):
        print(f"ERROR: Path not found: {path_input}")
        return
    
    # Collect files to scan
    json_files = []
    if os.path.isfile(path_input):
        json_files = [path_input]
    elif os.path.isdir(path_input):
        json_files = list(Path(path_input).glob('**/*.json'))
    
    if not json_files:
        print("No JSON files found")
        return
    
    print(f"\nFound {len(json_files)} JSON file(s) to scan")
    
    # Ask mode
    mode = input("\nRun mode: (s)can only, (f)ix issues, (d)ry-run fix [s/f/d]: ").strip().lower()
    
    if mode not in ['s', 'f', 'd']:
        mode = 's'
    
    dry_run = (mode == 'd')
    should_fix = (mode in ['f', 'd'])
    
    print("\n" + "=" * 70)
    print("Starting scan...")
    print("=" * 70)
    
    total_files_with_issues = 0
    total_issues = 0
    
    for json_file in json_files:
        scan_result = scan_json_file(str(json_file))
        
        if scan_result['issues_found']:
            total_files_with_issues += 1
            total_issues += len(scan_result['issues_found'])
            
            if should_fix:
                fix_json_file(scan_result, api_key, dry_run)
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total files scanned: {len(json_files)}")
    print(f"Files with issues: {total_files_with_issues}")
    print(f"Total locations with issues: {total_issues}")
    
    if dry_run:
        print("\n[DRY RUN] No changes were made")
    elif should_fix:
        print("\n✅ All fixes applied!")
    else:
        print("\n[SCAN ONLY] Run with 'fix' mode to apply corrections")


if __name__ == "__main__":
    main()

