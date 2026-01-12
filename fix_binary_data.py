#!/usr/bin/env python3
"""
Script to fix binary data issues in JSON files and update Turso database
"""

import json
import re
import os
import sys
from pathlib import Path

def fix_binary_data_in_text(text):
    """
    Fix binary data markers in text by replacing them with proper Unicode characters
    """
    if not text:
        return text
    
    # Pattern to match <binary data, 1 bytes> followed by other characters
    # This appears to be corrupted Sinhala text where some characters got converted to binary markers
    
    # Common patterns we can see from the context:
    # ප<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>තිසංඛ should be ප්‍රතිසංඛ
    # ප<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>හාණය should be ප්‍රහාණය
    
    # Replace the specific patterns we can identify
    fixes = [
        # ප්‍රතිසංඛ pattern
        (r'ප<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>තිසංඛ', 'ප්‍රතිසංඛ'),
        # ප්‍රහාණ pattern  
        (r'ප<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>හාණ', 'ප්‍රහාණ'),
        # ශෛක්‍ෂ pattern
        (r'ශෛක<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>ෂ', 'ශෛක්‍ෂ'),
        # General pattern - try to reconstruct common Sinhala conjuncts
        (r'<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>', '්‍ර'),
        (r'<binary data, 1 bytes><binary data, 1 bytes>', '්‍'),
        (r'<binary data, 1 bytes>', '්'),
    ]
    
    result = text
    for pattern, replacement in fixes:
        result = re.sub(pattern, replacement, result)
    
    return result

def fix_json_file(file_path):
    """
    Fix binary data issues in a JSON file
    """
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Recursively fix all string values in the JSON
        def fix_recursive(obj):
            if isinstance(obj, dict):
                return {k: fix_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [fix_recursive(item) for item in obj]
            elif isinstance(obj, str):
                return fix_binary_data_in_text(obj)
            else:
                return obj
        
        fixed_data = fix_recursive(data)
        
        # Write back the fixed data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Fixed: {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """
    Main function to fix binary data in JSON files
    """
    # Find all JSON files with binary data issues
    json_files = []
    
    # Search in the Anguttara directory
    anguttara_path = Path("Aṅguttaranikāyo")
    if anguttara_path.exists():
        json_files.extend(anguttara_path.rglob("*.json"))
    
    # Also check other directories that might have JSON files
    for directory in ["Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            json_files.extend(dir_path.rglob("*.json"))
    
    if not json_files:
        print("No JSON files found to process")
        return
    
    print(f"Found {len(json_files)} JSON files to check")
    
    fixed_count = 0
    for json_file in json_files:
        # Check if file contains binary data markers
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '<binary data, 1 bytes>' in content:
                    if fix_json_file(json_file):
                        fixed_count += 1
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
    
    print(f"\n✓ Fixed {fixed_count} files with binary data issues")

if __name__ == "__main__":
    main()