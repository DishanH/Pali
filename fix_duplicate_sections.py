"""
Fix duplicate sections in JSON files
This script removes duplicate section entries from the identified files
"""

import json
from pathlib import Path
from collections import defaultdict

# Files with duplicates identified
DUPLICATE_FILES = [
    {
        'path': 'Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters/mn.3.1-Devadahavaggo.json',
        'chapter_id': 'mn.3.1',
        'duplicate_section': 2
    },
    {
        'path': 'Saṃyuttanikāyo/Nidānavaggo/chapters/sn.2.1-Nidānasaṃyuttaṃ.json',
        'chapter_id': 'sn.2.1',
        'duplicate_section': 73
    },
    {
        'path': 'Saṃyuttanikāyo/Saḷāyatanavaggo/chapters/sn.4.1-Saḷāyatanasaṃyuttaṃ.json',
        'chapter_id': 'sn.4.1',
        'duplicate_section': 1
    }
]


def fix_duplicates_in_file(file_path, duplicate_section_num):
    """Remove duplicate sections from a file, keeping only the first occurrence"""
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"\n📄 Processing: {file_path.name}")
    
    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    sections = data.get("sections", [])
    original_count = len(sections)
    
    # Track which section numbers we've seen
    seen_numbers = set()
    unique_sections = []
    duplicates_removed = 0
    
    for section in sections:
        section_num = section.get("number")
        
        if section_num not in seen_numbers:
            seen_numbers.add(section_num)
            unique_sections.append(section)
        else:
            duplicates_removed += 1
            print(f"  🗑️  Removing duplicate section {section_num}")
            print(f"      Title: {section.get('paliTitle', 'N/A')}")
    
    # Update the data
    data["sections"] = unique_sections
    
    # Create backup
    backup_path = file_path.with_suffix('.json.backup')
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  💾 Backup saved: {backup_path.name}")
    
    # Write the fixed file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Fixed: {original_count} → {len(unique_sections)} sections")
    print(f"  ✅ Removed {duplicates_removed} duplicate(s)")
    
    return True


def main():
    """Fix all duplicate files"""
    
    print("="*80)
    print("FIXING DUPLICATE SECTIONS")
    print("="*80)
    
    success_count = 0
    
    for file_info in DUPLICATE_FILES:
        try:
            if fix_duplicates_in_file(file_info['path'], file_info['duplicate_section']):
                success_count += 1
        except Exception as e:
            print(f"❌ Error processing {file_info['path']}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(f"SUMMARY: Fixed {success_count}/{len(DUPLICATE_FILES)} files")
    print("="*80)
    
    if success_count == len(DUPLICATE_FILES):
        print("\n✅ All duplicates fixed!")
        print("\n📝 Next steps:")
        print("   1. Review the changes in the fixed files")
        print("   2. Run check_sections_simple.py again to verify")
        print("   3. Re-import the fixed files to Turso database")
    else:
        print("\n⚠️  Some files had issues. Please review the errors above.")


if __name__ == "__main__":
    main()
