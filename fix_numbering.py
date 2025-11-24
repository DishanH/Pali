"""
Fix numbering in chapter JSON files
Removes section numbers (80., 81., etc.) from the beginning of translations
"""

import sys
import os
import json
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def remove_numbering_from_text(text):
    """
    Remove section numbering from the beginning of text
    Examples:
    - "80 . Text here" -> "Text here"
    - "3. Cakkavattisuttaṃ\n\n80. Text" -> "3. Cakkavattisuttaṃ\n\nText"
    """
    if not text:
        return text
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove standalone numbering at start of line (e.g., "80 ." or "81.")
        # But keep chapter titles (e.g., "3. Cakkavattisuttaṃ")
        cleaned_line = re.sub(r'^\s*(\d+)\s*\.\s+(?!.*suttaṃ|.*suttantaṃ)', '', line)
        cleaned_lines.append(cleaned_line)
    
    return '\n'.join(cleaned_lines)


def fix_chapter_json(input_file, output_file=None):
    """
    Fix numbering in a chapter JSON file
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file (if None, overwrites input)
    """
    print(f"\n📖 Processing: {input_file}")
    
    # Read the JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Track changes
    changes_made = 0
    
    # Process each section
    if 'sections' in data:
        for i, section in enumerate(data['sections']):
            section_num = section.get('number', i+1)
            
            # Clean Pali text
            if 'pali' in section:
                original_pali = section['pali']
                cleaned_pali = remove_numbering_from_text(original_pali)
                if cleaned_pali != original_pali:
                    section['pali'] = cleaned_pali
                    changes_made += 1
                    print(f"  ✓ Section {section_num}: Cleaned Pali text")
            
            # Clean English text
            if 'english' in section:
                original_english = section['english']
                cleaned_english = remove_numbering_from_text(original_english)
                if cleaned_english != original_english:
                    section['english'] = cleaned_english
                    changes_made += 1
                    print(f"  ✓ Section {section_num}: Cleaned English text")
            
            # Clean Sinhala text
            if 'sinhala' in section:
                original_sinhala = section['sinhala']
                cleaned_sinhala = remove_numbering_from_text(original_sinhala)
                if cleaned_sinhala != original_sinhala:
                    section['sinhala'] = cleaned_sinhala
                    changes_made += 1
                    print(f"  ✓ Section {section_num}: Cleaned Sinhala text")
    
    if changes_made == 0:
        print("  ℹ️ No changes needed")
        return True
    
    # Write back to file
    output_path = output_file if output_file else input_file
    
    try:
        # Create backup of original
        if output_path == input_file:
            backup_path = input_file + '.backup'
            import shutil
            shutil.copy2(input_file, backup_path)
            print(f"  💾 Backup created: {backup_path}")
        
        # Write cleaned data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ Saved: {output_path}")
        print(f"  📊 Total changes: {changes_made}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error writing file: {e}")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fix numbering in chapter JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Fix a single file (creates backup)
  python fix_numbering.py Pāthikavaggapāḷi/chapters/dn3-Cakkavattisuttaṃ.json
  
  # Fix multiple files
  python fix_numbering.py Pāthikavaggapāḷi/chapters/dn*.json
  
  # Fix and save to different file
  python fix_numbering.py input.json --output output.json
  
  # Fix all chapters in directory
  python fix_numbering.py Pāthikavaggapāḷi/chapters/*.json
        '''
    )
    
    parser.add_argument('files', nargs='+', help='JSON file(s) to process')
    parser.add_argument('-o', '--output', help='Output file (for single file only)')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backup files')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔧 Fix Numbering in Chapter JSON Files")
    print("=" * 60)
    
    if len(args.files) > 1 and args.output:
        print("\n❌ Error: --output can only be used with a single input file")
        return 1
    
    success_count = 0
    error_count = 0
    
    for file_path in args.files:
        # Handle wildcards
        import glob
        matching_files = glob.glob(file_path)
        
        if not matching_files:
            print(f"\n⚠️ No files found matching: {file_path}")
            continue
        
        for matched_file in matching_files:
            if not os.path.exists(matched_file):
                print(f"\n❌ File not found: {matched_file}")
                error_count += 1
                continue
            
            output_file = args.output if args.output else None
            success = fix_chapter_json(matched_file, output_file)
            
            if success:
                success_count += 1
            else:
                error_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"✅ Success: {success_count} file(s)")
    if error_count > 0:
        print(f"❌ Errors: {error_count} file(s)")
    print("=" * 60)
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

