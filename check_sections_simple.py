"""
Simple check for duplicate and missing sections by comparing JSON files
This doesn't require database access - just checks the local files
"""

import json
from pathlib import Path
from collections import defaultdict

# Collection folders to check
COLLECTION_FOLDERS = [
    "Aṅguttaranikāyo",
    "Dīghanikāyo",
    "Majjhimanikāye",
    "Saṃyuttanikāyo"
]


def check_all_files():
    """Check all JSON files for issues"""
    
    print("="*80)
    print("CHECKING ALL JSON FILES FOR SECTION ISSUES")
    print("="*80)
    
    all_duplicates = []
    all_missing = []
    total_sections = 0
    total_chapters = 0
    
    for collection_folder in COLLECTION_FOLDERS:
        collection_path = Path(collection_folder)
        
        if not collection_path.exists():
            print(f"\n⏭️  Skipping {collection_folder} (folder not found)")
            continue
        
        print(f"\n{'='*80}")
        print(f"📂 Checking {collection_folder}")
        print(f"{'='*80}")
        
        # Get all book folders
        book_folders = [f for f in collection_path.iterdir() 
                       if f.is_dir() and f.name.lower() != "pdfs"]
        
        for book_folder in book_folders:
            chapters_folder = book_folder / "chapters"
            
            if not chapters_folder.exists():
                continue
            
            print(f"\n  📚 Book: {book_folder.name}")
            
            # Check each chapter file
            chapter_files = sorted(list(chapters_folder.glob("*.json")))
            
            for chapter_file in chapter_files:
                try:
                    with open(chapter_file, "r", encoding="utf-8") as f:
                        chapter_data = json.load(f)
                    
                    chapter_id = chapter_data.get("id")
                    sections = chapter_data.get("sections", [])
                    
                    if not sections:
                        print(f"    ⚠️  {chapter_file.name}: No sections found")
                        continue
                    
                    total_chapters += 1
                    total_sections += len(sections)
                    
                    # Check for duplicate section numbers
                    section_numbers = [s.get("number") for s in sections]
                    duplicates = find_duplicates(section_numbers)
                    
                    if duplicates:
                        print(f"    ❌ {chapter_file.name}: DUPLICATE section numbers found!")
                        for num, count in duplicates.items():
                            print(f"       Section {num} appears {count} times")
                            all_duplicates.append({
                                'file': str(chapter_file),
                                'chapter_id': chapter_id,
                                'section_number': num,
                                'count': count
                            })
                    
                    # Check for missing section numbers
                    if section_numbers:
                        min_num = min(section_numbers)
                        max_num = max(section_numbers)
                        expected = set(range(min_num, max_num + 1))
                        actual = set(section_numbers)
                        missing = sorted(expected - actual)
                        
                        if missing:
                            print(f"    ⚠️  {chapter_file.name}: Missing sections {missing}")
                            all_missing.append({
                                'file': str(chapter_file),
                                'chapter_id': chapter_id,
                                'missing_numbers': missing,
                                'range': f"{min_num}-{max_num}",
                                'total_sections': len(sections)
                            })
                        else:
                            print(f"    ✅ {chapter_file.name}: {len(sections)} sections (complete)")
                
                except Exception as e:
                    print(f"    ❌ Error reading {chapter_file.name}: {e}")
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total chapters checked: {total_chapters}")
    print(f"Total sections found: {total_sections}")
    print(f"Files with duplicate sections: {len(all_duplicates)}")
    print(f"Files with missing sections: {len(all_missing)}")
    
    # Save detailed report
    report = {
        "summary": {
            "total_chapters": total_chapters,
            "total_sections": total_sections,
            "files_with_duplicates": len(all_duplicates),
            "files_with_missing": len(all_missing)
        },
        "duplicates": all_duplicates,
        "missing_sections": all_missing
    }
    
    report_path = "file_section_check_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    if all_duplicates:
        print("\n" + "="*80)
        print("DUPLICATE DETAILS")
        print("="*80)
        for dup in all_duplicates:
            print(f"\nFile: {dup['file']}")
            print(f"  Chapter ID: {dup['chapter_id']}")
            print(f"  Section {dup['section_number']} appears {dup['count']} times")
    
    if all_missing:
        print("\n" + "="*80)
        print("MISSING SECTIONS DETAILS")
        print("="*80)
        for miss in all_missing:
            print(f"\nFile: {miss['file']}")
            print(f"  Chapter ID: {miss['chapter_id']}")
            print(f"  Range: {miss['range']}")
            print(f"  Missing: {miss['missing_numbers']}")
    
    return report


def find_duplicates(numbers):
    """Find duplicate numbers in a list"""
    counts = defaultdict(int)
    for num in numbers:
        counts[num] += 1
    
    return {num: count for num, count in counts.items() if count > 1}


if __name__ == "__main__":
    check_all_files()
    print("\n✅ Check complete!")
