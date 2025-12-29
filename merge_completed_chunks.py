#!/usr/bin/env python3
"""
Simple Merge Script for Completed Chunks
Works with chunk_XX.json files that have been translated
"""

import json
from pathlib import Path

def merge_all_chunks():
    """Merge all translated chunk files into bulk_translations.json"""
    
    # Find all chunk files (chunk_01.json, chunk_02.json, etc.)
    chunk_files = []
    for i in range(1, 34):  # We have 33 chunks
        chunk_file = Path(f"chunk_{i:02d}.json")
        if chunk_file.exists():
            chunk_files.append(chunk_file)
    
    if not chunk_files:
        print("❌ No chunk files found")
        print("Expected files like: chunk_01.json, chunk_02.json, etc.")
        return False
    
    print(f"📊 Found {len(chunk_files)} chunk files")
    
    # Load all chunks
    all_translations = []
    total_translated = 0
    
    for chunk_file in chunk_files:
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
            
            # Count how many are translated in this chunk
            translated_in_chunk = 0
            for item in chunk_data:
                if item.get('english', '').strip() or item.get('sinhala', '').strip():
                    translated_in_chunk += 1
            
            all_translations.extend(chunk_data)
            total_translated += translated_in_chunk
            
            print(f"  ✓ {chunk_file.name}: {len(chunk_data)} terms, {translated_in_chunk} translated")
            
        except Exception as e:
            print(f"  ❌ Error loading {chunk_file.name}: {e}")
            return False
    
    print(f"\n📊 Total: {len(all_translations)} terms, {total_translated} translated")
    
    if total_translated == 0:
        print("❌ No translations found in chunk files")
        return False
    
    # Load the main bulk_translations.json file
    bulk_file = Path("bulk_translations.json")
    if not bulk_file.exists():
        print("❌ Main bulk_translations.json file not found")
        return False
    
    with open(bulk_file, 'r', encoding='utf-8') as f:
        main_data = json.load(f)
    
    # Apply translations
    updated_count = 0
    for item in all_translations:
        pali = item['pali']
        english = item.get('english', '').strip()
        sinhala = item.get('sinhala', '').strip()
        
        if pali in main_data['translations']:
            if english:
                main_data['translations'][pali]['english'] = english
                updated_count += 1
            if sinhala:
                main_data['translations'][pali]['sinhala'] = sinhala
                if english:  # Don't double count if both languages provided
                    pass
                else:
                    updated_count += 1
    
    # Save updated file
    with open(bulk_file, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Merge complete!")
    print(f"📊 Updated {updated_count} translation entries in {bulk_file.name}")
    print(f"🎉 Ready to run: python apply_bulk_translations.py")
    
    return True

def main():
    print("=" * 60)
    print("Merge Completed Chunks")
    print("=" * 60)
    
    success = merge_all_chunks()
    
    if success:
        print(f"\n💡 Next step: Run 'python apply_bulk_translations.py' to apply translations to source files")
    else:
        print(f"\n❌ Merge failed. Please check the error messages above.")

if __name__ == "__main__":
    main()