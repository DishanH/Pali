"""
Test script to demonstrate recursive directory search functionality
"""

import os
import sys
import glob

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_recursive_search(directory: str, file_pattern: str = "*.json"):
    """
    Test the recursive search functionality without actually processing files
    """
    print("=" * 70)
    print("Testing Recursive Directory Search")
    print("=" * 70)
    
    print(f"\n📂 Base Directory: {directory}")
    print(f"🔍 File Pattern: {file_pattern}")
    
    if not os.path.exists(directory):
        print(f"\n❌ ERROR: Directory not found: {directory}")
        return
    
    # Find all 'chapters' subdirectories recursively
    print(f"\n🔍 Searching for 'chapters' directories...")
    chapters_dirs = []
    
    for root, dirs, files in os.walk(directory):
        if 'chapters' in dirs:
            chapters_path = os.path.join(root, 'chapters')
            chapters_dirs.append(chapters_path)
    
    if not chapters_dirs:
        print(f"❌ No 'chapters' directories found in {directory}")
        return
    
    print(f"\n✅ Found {len(chapters_dirs)} chapters directories:")
    for chapters_dir in sorted(chapters_dirs):
        rel_path = os.path.relpath(chapters_dir, directory)
        print(f"   📁 {rel_path}")
    
    # Collect all JSON files from all chapters directories
    print(f"\n📄 Searching for files matching '{file_pattern}'...")
    all_files = []
    
    for chapters_dir in sorted(chapters_dirs):
        matching_files = sorted(glob.glob(os.path.join(chapters_dir, file_pattern)))
        if matching_files:
            rel_path = os.path.relpath(chapters_dir, directory)
            print(f"\n   📁 {rel_path}")
            print(f"      Found {len(matching_files)} files:")
            for f in matching_files:
                filename = os.path.basename(f)
                print(f"      ✓ {filename}")
            all_files.extend(matching_files)
        else:
            rel_path = os.path.relpath(chapters_dir, directory)
            print(f"\n   📁 {rel_path}")
            print(f"      ⚠ No files matching pattern")
    
    print(f"\n{'=' * 70}")
    print(f"SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total directories searched: {len(chapters_dirs)}")
    print(f"Total files found: {len(all_files)}")
    print(f"{'=' * 70}")
    
    if all_files:
        print(f"\n📋 Files would be processed in this order:")
        for idx, f in enumerate(all_files, 1):
            rel_path = os.path.relpath(f, directory)
            print(f"   {idx:2d}. {rel_path}")


if __name__ == "__main__":
    print("\nThis script demonstrates the recursive search functionality")
    print("without actually translating anything.\n")
    
    # Test 1: Search all Majjhima Nikāya
    print("\n" + "=" * 70)
    print("TEST 1: All Majjhima Nikāya files")
    print("=" * 70)
    test_recursive_search("Majjhimanikāye", "mn*.json")
    
    # Test 2: Only Uparipaṇṇāsapāḷi files
    print("\n\n" + "=" * 70)
    print("TEST 2: Only Uparipaṇṇāsapāḷi files (mn.3.*)")
    print("=" * 70)
    test_recursive_search("Majjhimanikāye", "mn.3.*.json")
    
    # Test 3: All JSON files
    print("\n\n" + "=" * 70)
    print("TEST 3: All JSON files in Majjhima Nikāya")
    print("=" * 70)
    test_recursive_search("Majjhimanikāye", "*.json")

