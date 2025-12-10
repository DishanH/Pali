"""
Remove Duplicate Consecutive Vagga Fields in JSON Files
Keeps vagga only at the start and when it changes
"""

import json
import os
import glob
from pathlib import Path


def remove_duplicate_vaggas(json_path: str) -> dict:
    """
    Remove duplicate consecutive vagga fields from a JSON file
    
    Args:
        json_path: Path to the JSON file
    
    Returns:
        Statistics about the operation
    """
    print(f"\nProcessing: {os.path.basename(json_path)}")
    
    # Load JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    
    sections = chapter_data.get('sections', [])
    
    if not sections:
        print("  No sections found")
        return {'removed': 0, 'kept': 0}
    
    stats = {'removed': 0, 'kept': 0}
    previous_vagga = None
    
    for i, section in enumerate(sections):
        current_vagga = section.get('vagga', '').strip()
        
        if not current_vagga:
            continue
        
        # Keep vagga if it's the first one or if it changed
        if i == 0 or current_vagga != previous_vagga:
            stats['kept'] += 1
            previous_vagga = current_vagga
            print(f"  ✓ Section {i+1}: Keeping vagga '{current_vagga}'")
        else:
            # Remove duplicate vagga
            del section['vagga']
            # Also remove translations if they exist
            if 'vaggaEnglish' in section:
                del section['vaggaEnglish']
            if 'vaggaSinhala' in section:
                del section['vaggaSinhala']
            stats['removed'] += 1
            print(f"  ✗ Section {i+1}: Removed duplicate vagga '{current_vagga}'")
    
    # Save the updated file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    print(f"  Summary: {stats['kept']} kept, {stats['removed']} removed")
    
    return stats


def process_directory(directory: str, recursive: bool = True):
    """
    Process all JSON files in a directory
    
    Args:
        directory: Base directory to search
        recursive: If True, search all subdirectories for 'chapters' folders
    """
    json_files = []
    
    if recursive:
        print(f"\n🔍 Searching for 'chapters' directories in: {directory}")
        chapters_dirs = []
        
        for root, dirs, files in os.walk(directory):
            if 'chapters' in dirs:
                chapters_path = os.path.join(root, 'chapters')
                chapters_dirs.append(chapters_path)
        
        if not chapters_dirs:
            print(f"No 'chapters' directories found in {directory}")
            return
        
        print(f"Found {len(chapters_dirs)} chapters directories")
        
        # Collect all JSON files from all chapters directories
        for chapters_dir in sorted(chapters_dirs):
            matching_files = sorted(glob.glob(os.path.join(chapters_dir, '*.json')))
            json_files.extend(matching_files)
    else:
        json_files = sorted(glob.glob(os.path.join(directory, '*.json')))
    
    if not json_files:
        print(f"No JSON files found")
        return
    
    print(f"\n📚 Total: {len(json_files)} JSON files to process")
    print("=" * 60)
    
    total_stats = {'removed': 0, 'kept': 0, 'files_processed': 0}
    
    for json_file in json_files:
        try:
            stats = remove_duplicate_vaggas(json_file)
            total_stats['files_processed'] += 1
            total_stats['removed'] += stats['removed']
            total_stats['kept'] += stats['kept']
        except Exception as e:
            print(f"\n❌ Error processing {json_file}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Files processed: {total_stats['files_processed']}")
    print(f"Vaggas kept: {total_stats['kept']}")
    print(f"Vaggas removed: {total_stats['removed']}")
    print(f"{'='*60}")


def main():
    """Main execution function"""
    print("=" * 60)
    print("Remove Duplicate Vagga Fields")
    print("=" * 60)
    
    directory = input("\nEnter directory path (default: Saṃyuttanikāyo): ").strip()
    
    if not directory:
        directory = "Saṃyuttanikāyo"
    
    if not os.path.exists(directory):
        print(f"ERROR: Directory not found: {directory}")
        return
    
    recursive_input = input("Search recursively for 'chapters' folders? (y/n, default: y): ").strip().lower()
    recursive = recursive_input != 'n'
    
    try:
        process_directory(directory, recursive=recursive)
        print("\n✓ Process completed!")
    except Exception as e:
        print(f"\nERROR: {e}")
        return


if __name__ == "__main__":
    main()
