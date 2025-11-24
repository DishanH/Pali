"""
Quick script to verify all file paths work correctly
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print("=" * 60)
print("Path Verification Script")
print("=" * 60)

# Test paths
paths_to_check = [
    os.path.join("Pāthikavaggapāḷi", "Pāthikavaggapāḷi_pali_extracted.txt"),
    os.path.join("Pāthikavaggapāḷi", "book.json"),
    os.path.join("Pāthikavaggapāḷi", "sample.txt"),
    os.path.join("Pāthikavaggapāḷi", "chapters", "dn1-Pāthikasuttaṃ.json"),
]

print("\nChecking file paths...")
all_good = True

for path in paths_to_check:
    exists = os.path.exists(path)
    status = "✓ EXISTS" if exists else "✗ NOT FOUND"
    print(f"{status}: {path}")
    if not exists and "chapters" not in path:
        all_good = False

# Check if we can create paths without warnings
print("\nTesting path construction...")
try:
    test_path = os.path.join("Pāthikavaggapāḷi", "chapters", "test-file.json")
    print(f"✓ Path construction works: {test_path}")
except Exception as e:
    print(f"✗ Path construction failed: {e}")
    all_good = False

# Test reading book.json
print("\nTesting book.json reading...")
try:
    book_file = os.path.join("Pāthikavaggapāḷi", "book.json")
    with open(book_file, 'r', encoding='utf-8') as f:
        import json
        book_data = json.load(f)
    print(f"✓ Successfully loaded book.json: {book_data['totalChapters']} chapters")
except Exception as e:
    print(f"✗ Failed to read book.json: {e}")
    all_good = False

# Test reading Pali text
print("\nTesting Pali text reading...")
try:
    pali_file = os.path.join("Pāthikavaggapāḷi", "Pāthikavaggapāḷi_pali_extracted.txt")
    with open(pali_file, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f"✓ Successfully loaded Pali text: {len(text)} characters")
except Exception as e:
    print(f"✗ Failed to read Pali text: {e}")
    all_good = False

print("\n" + "=" * 60)
if all_good:
    print("✅ All path tests passed!")
    print("\nThe translator should work without warnings now.")
    print("\nTo run the translator:")
    print("  $env:GOOGLE_API_KEY=\"your-key\"")
    print("  python translator.py")
else:
    print("⚠️ Some issues found. Check the output above.")
print("=" * 60)

