#!/usr/bin/env python3
"""
Chunk Footer Translations Script
Splits the bulk_footer_translations.json file into smaller chunks for easier translation.
"""

import json
from pathlib import Path
import math

def chunk_footer_translations(input_file="bulk_footer_translations.json", chunk_size=50):
    """Split footer translations into smaller chunks"""
    
    # Load the main file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_file}")
        print("Please run extract_missing_footers.py first")
        return False
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translations = data.get('translations', {})
        if not translations:
            print("❌ No translations found in the input file")
            return False
        
        # Convert to list for chunking
        translation_items = []
        for pali_text, info in translations.items():
            translation_items.append({
                "pali": pali_text,
                "english": "",
                "sinhala": "",
                "contexts": info.get('contexts', []),
                "usage_count": info.get('usage_count', 1),
                "originally_needed": info.get('originally_needed', {"english": True, "sinhala": True})
            })
        
        # Calculate number of chunks
        total_items = len(translation_items)
        num_chunks = math.ceil(total_items / chunk_size)
        
        print(f"📊 Splitting {total_items} footer translations into {num_chunks} chunks of {chunk_size} items each")
        
        # Create chunks
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min(start_idx + chunk_size, total_items)
            chunk_items = translation_items[start_idx:end_idx]
            
            # Create chunk file
            chunk_filename = f"footer_chunk_{i+1:02d}.json"
            with open(chunk_filename, 'w', encoding='utf-8') as f:
                json.dump(chunk_items, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ Created {chunk_filename} with {len(chunk_items)} items")
        
        print(f"\n✅ Chunking complete!")
        print(f"📁 Created {num_chunks} chunk files: footer_chunk_01.json to footer_chunk_{num_chunks:02d}.json")
        print(f"\n💡 Next steps:")
        print(f"   1. Translate each chunk file using your preferred translation tool")
        print(f"   2. Run merge_completed_footer_chunks.py to merge them back")
        print(f"   3. Run apply_bulk_footer_translations.py to apply the translations")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return False

def main():
    import sys
    
    input_file = "bulk_footer_translations.json"
    chunk_size = 50
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        chunk_size = int(sys.argv[2])
    
    print("=" * 60)
    print("Footer Translation Chunker")
    print("=" * 60)
    
    chunk_footer_translations(input_file, chunk_size)

if __name__ == "__main__":
    main()