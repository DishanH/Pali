"""
Fix literal ZWJ text in JSON files by replacing with actual Zero-Width Joiner (U+200D)
Handles multiple formats: <ZWJ>, [ZWJ], #zwj;, &#8205;
"""

import json
import os
import glob
from pathlib import Path
import re

def fix_zwj_in_file(json_path: str) -> tuple:
    """
    Replace all ZWJ literal variations with actual U+200D character
    
    Handles:
    - <ZWJ>
    - [ZWJ]
    - #zwj;
    - &#8205; (HTML entity)
    - &zwj; (HTML entity)
    
    Returns:
        (fixed_count, file_was_modified)
    """
    print(f"\nChecking: {json_path}")
    
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count all variations
    variations = {
        '<ZWJ>': content.count('<ZWJ>'),
        '[ZWJ]': content.count('[ZWJ]'),
        '#zwj;': content.count('#zwj;'),
        '#ZWJ#': content.count('#ZWJ#'),
        '_ZWJ_': content.count('_ZWJ_'),
        '&#8205;': content.count('&#8205;'),
        '&zwj;': content.count('&zwj;')
    }
    
    total_count = sum(variations.values())
    
    if total_count == 0:
        print(f"  ✓ No ZWJ literals found")
        return 0, False
    
    # Report what was found
    print(f"  ⚠ Found {total_count} ZWJ literals:")
    for variant, count in variations.items():
        if count > 0:
            print(f"    - {variant}: {count}")
    
    # Replace all variations with actual Zero-Width Joiner
    fixed_content = content
    fixed_content = fixed_content.replace('<ZWJ>', '\u200D')
    fixed_content = fixed_content.replace('[ZWJ]', '\u200D')
    fixed_content = fixed_content.replace('#zwj;', '\u200D')
    fixed_content = fixed_content.replace('#ZWJ#', '\u200D')
    fixed_content = fixed_content.replace('_ZWJ_', '\u200D')
    fixed_content = fixed_content.replace('&#8205;', '\u200D')
    fixed_content = fixed_content.replace('&zwj;', '\u200D')
    
    # Save fixed file
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"  ✓ Fixed {total_count} occurrences")
    return total_count, True

def main():
    """Fix all JSON chapter files"""
    print("="*60)
    print("Fixing literal <ZWJ> text in JSON files")
    print("="*60)
    
    # Find all JSON chapter files
    json_files = []
    for pattern in ['*/chapters/*.json', '*/chapters/*/*.json']:
        json_files.extend(glob.glob(pattern, recursive=True))
    
    if not json_files:
        print("\n❌ No JSON files found!")
        return
    
    print(f"\nFound {len(json_files)} JSON files")
    
    total_fixed = 0
    files_modified = 0
    
    for json_path in sorted(json_files):
        fixed_count, was_modified = fix_zwj_in_file(json_path)
        total_fixed += fixed_count
        if was_modified:
            files_modified += 1
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Files checked: {len(json_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total <ZWJ> literals fixed: {total_fixed}")
    print(f"\n✓ All files fixed!")

if __name__ == '__main__':
    main()
