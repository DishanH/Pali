"""
Batch PDF Extraction Script for Aṅguttara Nikāya
Extracts all nipāta PDFs and creates structured JSON files
"""

import sys
import os
from pathlib import Path

# Import the correct Aṅguttara extractor class
from extract_anguttara_correct import AnguttaraVaggaExtractor

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def main():
    """Extract all Aṅguttara Nikāya PDFs"""
    
    # Configuration for all Aṅguttara Nikāya books
    books = [
        {
            'name': 'Ekakanipātapāḷi',
            'pali_title': 'Ekakanipātapāḷi',
            'pdf_filename': 'Ekakanipātapāḷi.pdf',
            'nipata_num': 1,  # Book of Ones
            'starting_an': 1  # AN 1.1, 1.2, etc.
        },
        {
            'name': 'Dukanipātapāḷi',
            'pali_title': 'Dukanipātapāḷi',
            'pdf_filename': 'Dukanipātapāḷi.pdf',
            'nipata_num': 2,  # Book of Twos
            'starting_an': 1  # AN 2.1, 2.2, etc.
        },
        {
            'name': 'Tikanipātapāḷi',
            'pali_title': 'Tikanipātapāḷi',
            'pdf_filename': 'Tikanipātapāḷi.pdf',
            'nipata_num': 3,  # Book of Threes
            'starting_an': 1  # AN 3.1, 3.2, etc.
        },
        {
            'name': 'Catukkanipātapāḷi',
            'pali_title': 'Catukkanipātapāḷi',
            'pdf_filename': 'Catukkanipātapāḷi.pdf',
            'nipata_num': 4,  # Book of Fours
            'starting_an': 1  # AN 4.1, 4.2, etc.
        },
        {
            'name': 'Pañcakanipātapāḷi',
            'pali_title': 'Pañcakanipātapāḷi',
            'pdf_filename': 'Pañcakanipātapāḷi.pdf',
            'nipata_num': 5,  # Book of Fives
            'starting_an': 1  # AN 5.1, 5.2, etc.
        },
        {
            'name': 'Chakkanipātapāḷi',
            'pali_title': 'Chakkanipātapāḷi',
            'pdf_filename': 'Chakkanipātapāḷi.pdf',
            'nipata_num': 6,  # Book of Sixes
            'starting_an': 1  # AN 6.1, 6.2, etc.
        },
        {
            'name': 'Sattakanipātapāḷi',
            'pali_title': 'Sattakanipātapāḷi',
            'pdf_filename': 'Sattakanipātapāḷi.pdf',
            'nipata_num': 7,  # Book of Sevens
            'starting_an': 1  # AN 7.1, 7.2, etc.
        },
        {
            'name': 'Aṭṭhakanipātapāḷi',
            'pali_title': 'Aṭṭhakanipātapāḷi',
            'pdf_filename': 'Aṭṭhakanipātapāḷi.pdf',
            'nipata_num': 8,  # Book of Eights
            'starting_an': 1  # AN 8.1, 8.2, etc.
        },
        {
            'name': 'Navakanipātapāḷi',
            'pali_title': 'Navakanipātapāḷi',
            'pdf_filename': 'Navakanipātapāḷi.pdf',
            'nipata_num': 9,  # Book of Nines
            'starting_an': 1  # AN 9.1, 9.2, etc.
        },
        {
            'name': 'Dasakanipātapāḷi',
            'pali_title': 'Dasakanipātapāḷi',
            'pdf_filename': 'Dasakanipātapāḷi.pdf',
            'nipata_num': 10,  # Book of Tens
            'starting_an': 1  # AN 10.1, 10.2, etc.
        },
        {
            'name': 'Ekādasakanipātapāḷi',
            'pali_title': 'Ekādasakanipātapāḷi',
            'pdf_filename': 'Ekādasakanipātapāḷi.pdf',
            'nipata_num': 11,  # Book of Elevens
            'starting_an': 1  # AN 11.1, 11.2, etc.
        }
    ]
    
    base_pdf_dir = r"Aṅguttaranikāyo\pdfs"
    base_output_dir = r"Aṅguttaranikāyo"
    
    # Verify base directories exist
    if not os.path.exists(base_pdf_dir):
        print(f"❌ Error: PDF directory not found: {base_pdf_dir}")
        return
    
    print("=" * 80)
    print("AṄGUTTARA NIKĀYA BATCH EXTRACTION")
    print("=" * 80)
    print(f"\nProcessing {len(books)} nipāta PDFs...")
    print(f"PDF directory: {base_pdf_dir}")
    print(f"Output directory: {base_output_dir}\n")
    
    successful = 0
    failed = 0
    skipped = 0
    
    for i, book_info in enumerate(books, 1):
        print("\n" + "=" * 80)
        print(f"[{i}/{len(books)}] {book_info['name']}")
        print("=" * 80)
        
        pdf_path = os.path.join(base_pdf_dir, book_info['pdf_filename'])
        output_dir = os.path.join(base_output_dir, book_info['name'])
        
        # Check if PDF exists
        if not os.path.exists(pdf_path):
            print(f"⚠️  Skipping: PDF not found at {pdf_path}")
            skipped += 1
            continue
        
        # Create book config
        book_config = {
            'name': book_info['name'],
            'pali_title': book_info['pali_title'],
            'english_title': '',
            'sinhala_title': '',
            'nipata_num': book_info['nipata_num'],
            'starting_an': book_info['starting_an']
        }
        
        try:
            # Create extractor and process
            extractor = AnguttaraVaggaExtractor(pdf_path, output_dir, book_config)
            extractor.process()
            successful += 1
            
        except Exception as e:
            print(f"\n❌ Error processing {book_info['name']}: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Final summary
    print("\n" + "=" * 80)
    print("BATCH EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\n✅ Successful: {successful}/{len(books)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(books)}")
    if skipped > 0:
        print(f"⚠️  Skipped: {skipped}/{len(books)}")
    print(f"\nAll output saved to: {base_output_dir}")


if __name__ == "__main__":
    main()
