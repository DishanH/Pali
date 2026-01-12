#!/usr/bin/env python3
"""
Script to fix Unicode escape sequences in JSON files
"""

import json
import re
import os
import sys
from pathlib import Path

def fix_unicode_escapes_in_text(text):
    """
    Fix Unicode escape sequences in text by converting them to actual Unicode characters
    """
    if not text:
        return text
    
    # Fix common Sinhala Unicode escape sequences
    # \\u0DCA is the Sinhala Al-lakuna (virama/halant) character
    # \\u200D is the Zero Width Joiner (ZWJ)
    
    # Replace escaped Unicode sequences with actual characters
    fixes = [
        # Sinhala Al-lakuna (virama) - ්
        (r'\\u0DCA', '\u0DCA'),
        # Zero Width Joiner
        (r'\\u200D', '\u200D'),
        # Other common Sinhala escapes
        (r'\\u0DCF', '\u0DCF'),  # Sinhala vowel sign Aela-pilla
        (r'\\u0DD9', '\u0DD9'),  # Sinhala vowel sign Kombuva
        (r'\\u0DDF', '\u0DDF'),  # Sinhala vowel sign Gayanukitta
    ]
    
    result = text
    for pattern, replacement in fixes:
        result = re.sub(pattern, replacement, result)
    
    return result

def fix_json_file(file_path):
    """
    Fix Unicode escape sequences in a JSON file
    """
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if file has Unicode escape issues
        content_str = json.dumps(data, ensure_ascii=False)
        if '\\u0DCA' not in content_str and '\\u200D' not in content_str:
            print(f"  ℹ️  No Unicode escape issues found")
            return False
        
        # Recursively fix all string values in the JSON
        def fix_recursive(obj):
            if isinstance(obj, dict):
                return {k: fix_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [fix_recursive(item) for item in obj]
            elif isinstance(obj, str):
                return fix_unicode_escapes_in_text(obj)
            else:
                return obj
        
        fixed_data = fix_recursive(data)
        
        # Write back the fixed data with proper Unicode handling
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Fixed Unicode escapes")
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {file_path}: {e}")
        return False

def main():
    """
    Main function to fix Unicode escape sequences
    """
    print("=" * 60)
    print("Unicode Escape Sequence Fix")
    print("=" * 60)
    
    # Find all JSON files
    json_files = []
    
    # Search in all collection directories
    for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            json_files.extend(dir_path.rglob("*.json"))
    
    if not json_files:
        print("No JSON files found to process")
        return
    
    print(f"Found {len(json_files)} JSON files to check")
    
    fixed_count = 0
    for json_file in json_files:
        # Check if file contains Unicode escape sequences
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '\\u0DCA' in content or '\\u200D' in content:
                    if fix_json_file(json_file):
                        fixed_count += 1
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
    
    print(f"\n✓ Fixed {fixed_count} files with Unicode escape issues")

if __name__ == "__main__":
    main()