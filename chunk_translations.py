#!/usr/bin/env python3
"""
Translation Chunker
Splits the bulk translation file into smaller chunks for easier processing
with external tools that have input limits.
"""

import json
import argparse
from pathlib import Path

def chunk_translations(input_file, chunk_size=200, output_format='simple'):
    """Split translations into chunks"""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Load data
    with open(input_path, 'r', encoding='utf-8') as f:
        if input_file.endswith('_simple.json'):
            data = json.load(f)
        else:
            # Full format
            full_data = json.load(f)
            data = []
            for pali, info in full_data.get('translations', {}).items():
                data.append({
                    'pali': pali,
                    'english': '',
                    'sinhala': '',
                    'usage_count': info.get('usage_count', 0),
                    'sample_context': info.get('contexts', [''])[0]
                })
    
    total_terms = len(data)
    num_chunks = (total_terms + chunk_size - 1) // chunk_size
    
    print(f"📊 Chunking {total_terms} terms into {num_chunks} chunks of {chunk_size} terms each")
    
    # Create chunks
    for i in range(0, total_terms, chunk_size):
        chunk_num = i // chunk_size + 1
        chunk_data = data[i:i + chunk_size]
        
        chunk_file = f"chunk_{chunk_num:02d}.json"
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Created {chunk_file} with {len(chunk_data)} terms")
    
    # Create instruction file
    with open("chunking_instructions.md", 'w', encoding='utf-8') as f:
        f.write(f"# Translation Chunks\n\n")
        f.write(f"Original file split into {num_chunks} chunks of ~{chunk_size} terms each.\n\n")
        f.write(f"## Files created:\n")
        for i in range(num_chunks):
            f.write(f"- `chunk_{i+1:02d}.json` (terms {i*chunk_size + 1}-{min((i+1)*chunk_size, total_terms)})\n")
        
        f.write(f"\n## Translation workflow:\n")
        f.write(f"1. Translate each chunk file using your preferred tool\n")
        f.write(f"2. Save completed translations as `chunk_XX_completed.json`\n")
        f.write(f"3. Run `python chunk_translations.py --merge` to combine all chunks\n")
        f.write(f"4. Run `python apply_bulk_translations.py` to apply to source files\n")
        
        f.write(f"\n## Sample prompt for external tools:\n")
        f.write(f"```\n")
        f.write(f"Please translate these Pali Buddhist terms to English and Sinhala.\n")
        f.write(f"Fill in the 'english' and 'sinhala' fields in the JSON.\n")
        f.write(f"Context: These are canonical Buddhist terms from Pali texts.\n")
        f.write(f"- Terms ending in 'suttaṃ' are discourse titles\n")
        f.write(f"- Terms ending in 'vaggo' are chapter names\n")
        f.write(f"- Use the 'sample_context' to understand usage\n")
        f.write(f"```\n")
    
    print(f"\n✅ Chunking complete!")
    print(f"📁 Created {num_chunks} chunk files and chunking_instructions.md")

def merge_chunks():
    """Merge completed chunk files back into the main translation file"""
    
    # Find all completed chunk files
    chunk_files = sorted(Path('.').glob('chunk_*_completed.json'))
    
    if not chunk_files:
        print("❌ No completed chunk files found")
        print("Expected files like: chunk_01_completed.json, chunk_02_completed.json, etc.")
        return
    
    print(f"📊 Found {len(chunk_files)} completed chunk files")
    
    # Load all chunks
    all_translations = []
    for chunk_file in chunk_files:
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
                all_translations.extend(chunk_data)
            print(f"  ✓ Loaded {chunk_file.name} with {len(chunk_data)} terms")
        except Exception as e:
            print(f"  ❌ Error loading {chunk_file.name}: {e}")
    
    if not all_translations:
        print("❌ No translations loaded from chunk files")
        return
    
    # Update the main bulk_translations.json file
    bulk_file = Path("bulk_translations.json")
    if not bulk_file.exists():
        print("❌ Main bulk_translations.json file not found")
        return
    
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
                updated_count += 1
    
    # Save updated file
    with open(bulk_file, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Merge complete!")
    print(f"📊 Updated {updated_count} translations in {bulk_file.name}")
    print(f"🎉 Ready to run: python apply_bulk_translations.py")

def main():
    parser = argparse.ArgumentParser(description='Chunk or merge translation files')
    parser.add_argument('--input', default='bulk_translations_simple.json',
                       help='Input translation file to chunk')
    parser.add_argument('--chunk-size', type=int, default=200,
                       help='Number of terms per chunk')
    parser.add_argument('--merge', action='store_true',
                       help='Merge completed chunks back into main file')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Translation Chunker")
    print("=" * 60)
    
    if args.merge:
        merge_chunks()
    else:
        chunk_translations(args.input, args.chunk_size)

if __name__ == "__main__":
    main()