"""
Batch PDF Extraction Script for Majjhima Nikāya
Extracts all Majjhima PDFs and creates structured JSON files
"""

import sys
import os
from pathlib import Path

# Import the Majjhima extractor class
from extract_majjhima_correct import MajjhimaVaggaExtractor

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def main():
    """Extract all Majjhima Nikāya PDFs"""
    
    # Configuration for all Majjhima Nikāya books
    books = [
        {
            'name': 'Mūlapaṇṇāsapāḷi',
            'pali_title': 'Mūlapaṇṇāsapāḷi',
            'pdf_filename': 'Mūlapaṇṇāsapāḷi.pdf',
            'book_num': 1,  # First 50 suttas
        },
        {
            'name': 'Majjhimapaṇṇāsapāḷi',
            'pali_title': 'Majjhimapaṇṇāsapāḷi',
            'pdf_filename': 'Majjhimapaṇṇāsapāḷi.pdf',
            'book_num': 2,  # Second 50 suttas
        },
        {
            'name': 'Uparipaṇṇāsapāḷi',
            'pali_title': 'Uparipaṇṇāsapāḷi',
            'pdf_filename': 'Uparipaṇṇāsapāḷi.pdf',
            'book_num': 3,  # Last 52 suttas
        }
    ]
    
    base_pdf_dir = r"Majjhimanikāye\pdfs"
    base_output_dir = r"Majjhimanikāye"
    
    # Verify base directories exist
    if not os.path.exists(base_pdf_dir):
        print(f"❌ Error: PDF directory not found: {base_pdf_dir}")
        return
    
    print("=" * 80)
    print("MAJJHIMA NIKĀYA BATCH EXTRACTION")
    print("=" * 80)
    print(f"\nProcessing {len(books)} Majjhima PDFs...")
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
            'book_num': book_info['book_num']
        }
        
        try:
            # Create extractor and process
            extractor = MajjhimaVaggaExtractor(pdf_path, output_dir, book_config)
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

