"""
Fix duplicate sections in the 3 JSON files
Removes duplicate section numbers, keeping only the first occurrence
"""

import json
from pathlib import Path
from collections import defaultdict

# The 3 files with duplicates
FILES_TO_FIX = [
    'Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters/mn.3.1-Devadahavaggo.json',
    'Saṃyuttanikāyo/Nidānavaggo/chapters/sn.2.1-Nidānasaṃyuttaṃ.json',
    'Saṃyuttanikāyo/Saḷāyatanavaggo/chapters/sn.4.1-Saḷāyatanasaṃyuttaṃ.json'
]


def fix_file(file_path):
    """Remove duplicate sections from a file"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"\n{'='*80}")
    print(f"Processing: {file_path.name}")
    print(f"{'='*80}")
    
    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    sections = data.get("sections", [])
    original_count = len(sections)
    
    print(f"Original sections: {original_count}")
    
    # Track which section numbers we've seen
    seen_numbers = set()
    unique_sections = []
    duplicates_removed = []
    
    for section in sections:
        section_num = section.get("number")
        
        if section_num not in seen_numbers:
            seen_numbers.add(section_num)
            unique_sections.append(section)
        else:
            duplicates_removed.append(section_num)
            print(f"  🗑️  Removing duplicate section {section_num}")
            pali_title = section.get('paliTitle', '')
            if pali_title:
                print(f"      Title: {pali_title}")
    
    # Update the data
    data["sections"] = unique_sections
    
    # Create backup
    backup_path = file_path.with_suffix('.json.backup')
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Backup saved: {backup_path.name}")
    
    # Write the fixed file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Fixed: {original_count} → {len(unique_sections)} sections")
    print(f"✅ Removed {len(duplicates_removed)} duplicate(s): {duplicates_removed}")
    
    return True


def main():
    """Fix all files"""
    print("="*80)
    print("FIXING DUPLICATE SECTIONS IN JSON FILES")
    print("="*80)
    
    success_count = 0
    
    for file_path in FILES_TO_FIX:
        try:
            if fix_file(file_path):
                success_count += 1
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(f"SUMMARY: Fixed {success_count}/{len(FILES_TO_FIX)} files")
    print("="*80)
    
    if success_count == len(FILES_TO_FIX):
        print("\n✅ All files fixed successfully!")
        print("\n📝 Next steps:")
        print("   1. Review the fixed files")
        print("   2. Run: python check_sections_simple.py")
        print("   3. Re-import to database if needed")
    else:
        print("\n⚠️  Some files had issues. Please review the errors above.")


if __name__ == "__main__":
    main()
