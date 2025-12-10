"""
Batch PDF Extraction Script for Jātakapāḷi
Extracts both Jātakapāḷi PDFs and creates structured JSON files
Combines both volumes into a single Jātakapāḷi folder
"""

import sys
import os
from pathlib import Path

# Import the Jātaka extractor class
from extract_jataka_correct import JatakaExtractor

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def main():
    """Extract both Jātakapāḷi PDFs into a combined folder"""
    
    # Configuration for both Jātakapāḷi volumes
    volumes = [
        {
            'name': 'Jātakapāḷi_1',
            'pdf_filename': 'Jātakapāḷi_1.pdf',
            'id_prefix': 'ja',
        },
        {
            'name': 'Jātakapāḷi_2',
            'pdf_filename': 'Jātakapāḷi_2.pdf',
            'id_prefix': 'ja',
        }
    ]
    
    base_pdf_dir = r"Khuddakanikāye\pdfs"
    # Combined output directory for both volumes
    output_dir = r"Khuddakanikāye\Jātakapāḷi"
    
    # Verify base directories exist
    if not os.path.exists(base_pdf_dir):
        print(f"❌ Error: PDF directory not found: {base_pdf_dir}")
        return
    
    print("=" * 80)
    print("JĀTAKAPĀḶI BATCH EXTRACTION")
    print("=" * 80)
    print(f"\nProcessing {len(volumes)} Jātakapāḷi volumes...")
    print(f"PDF directory: {base_pdf_dir}")
    print(f"Combined output directory: {output_dir}\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    successful = 0
    failed = 0
    skipped = 0
    all_vaggas = []
    
    for i, volume_info in enumerate(volumes, 1):
        print("\n" + "=" * 80)
        print(f"[{i}/{len(volumes)}] {volume_info['name']}")
        print("=" * 80)
        
        pdf_path = os.path.join(base_pdf_dir, volume_info['pdf_filename'])
        
        # Check if PDF exists
        if not os.path.exists(pdf_path):
            print(f"⚠️  Skipping: PDF not found at {pdf_path}")
            skipped += 1
            continue
        
        # Create book config
        book_config = {
            'name': 'Jātakapāḷi',
            'pali_title': 'Jātakapāḷi',
            'english_title': '',
            'sinhala_title': '',
            'id_prefix': volume_info['id_prefix'],
        }
        
        try:
            # Create extractor and process
            extractor = JatakaExtractor(pdf_path, output_dir, book_config)
            
            # Extract text
            print(f"\n[1/6] Extracting text from PDF...")
            extractor.full_text = extractor.extract_text_from_pdf()
            
            print(f"\n[2/6] Cleaning text...")
            extractor.full_text = extractor.clean_text(extractor.full_text)
            
            print(f"\n[3/6] Saving full extracted text...")
            # Save with volume-specific name
            filename = f"{volume_info['name']}_pali_extracted.txt"
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(extractor.full_text)
            print(f"✓ Saved full text to: {output_path}")
            
            print(f"\n[4/6] Detecting structure (Nipāta > Vagga)...")
            nipatas = extractor.detect_structure(extractor.full_text)
            
            # Adjust nipāta IDs to continue from previous volume
            if all_vaggas:
                last_id = all_vaggas[-1]['id']
                last_num = int(last_id.split('.')[1])
                for nipata in nipatas:
                    old_num = int(nipata['id'].split('.')[1])
                    new_num = last_num + old_num
                    nipata['id'] = f"{volume_info['id_prefix']}.{new_num}"
                    print(f"  ✓ Adjusted ID: {nipata['nipata_title']} -> {nipata['id']}")
            
            all_vaggas.extend(nipatas)
            
            print(f"\n[5/6] Finding nipāta boundaries...")
            boundaries = extractor.find_nipata_boundaries(extractor.full_text, nipatas)
            
            print(f"\n[6/6] Creating nipāta JSON files...")
            lines = extractor.full_text.split('\n')
            
            for start_line, end_line, nipata_info in boundaries:
                nipata_lines = lines[start_line:end_line]
                nipata_text = '\n'.join(nipata_lines)
                
                nipata_json = extractor.create_nipata_json(nipata_info, nipata_text)
                extractor.save_nipata_json(nipata_info, nipata_json)
            
            successful += 1
            
        except Exception as e:
            print(f"\n❌ Error processing {volume_info['name']}: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Create combined book.json
    if all_vaggas:
        print("\n" + "=" * 80)
        print("Creating combined book.json...")
        print("=" * 80)
        
        book_json = {
            "name": "Jātakapāḷi",
            "title": {
                "pali": "Jātakapāḷi",
                "english": "",
                "sinhala": ""
            },
            "chapters": [
                {
                    "id": nipata['id'],
                    "title": {
                        "pali": nipata['nipata_title'],
                        "english": "",
                        "sinhala": ""
                    }
                }
                for nipata in all_vaggas
            ]
        }
        
        import json
        output_path = os.path.join(output_dir, "book.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(book_json, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Saved combined book metadata: book.json ({len(all_vaggas)} vaggas)")
    
    # Final summary
    print("\n" + "=" * 80)
    print("BATCH EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\n✅ Successful: {successful}/{len(volumes)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(volumes)}")
    if skipped > 0:
        print(f"⚠️  Skipped: {skipped}/{len(volumes)}")
    print(f"\nAll output saved to: {output_dir}")
    print(f"Total vaggas extracted: {len(all_vaggas)}")


if __name__ == "__main__":
    main()
