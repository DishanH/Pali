"""
Batch PDF Extraction Script for Khuddaka Nikāya
Extracts all Khuddaka PDFs and creates structured JSON files
"""

import sys
import os
from pathlib import Path

# Import the Khuddaka extractor class
from extract_khuddaka_correct import KhuddakaExtractor

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def main():
    """Extract all Khuddaka Nikāya PDFs"""
    
    # Configuration for all Khuddaka Nikāya books
    books = [
        {
            'name': 'Khuddakapāṭhapāḷi',
            'pali_title': 'Khuddakapāṭhapāḷi',
            'pdf_filename': 'Khuddakapāṭhapāḷi.pdf',
            'id_prefix': 'khp',
        },
        {
            'name': 'Dhammapadapāḷi',
            'pali_title': 'Dhammapadapāḷi',
            'pdf_filename': 'Dhammapadapāḷi.pdf',
            'id_prefix': 'dhp',
        },
        {
            'name': 'Udānapāḷi',
            'pali_title': 'Udānapāḷi',
            'pdf_filename': 'Udānapāḷi.pdf',
            'id_prefix': 'ud',
        },
        {
            'name': 'Itivuttakapāḷi',
            'pali_title': 'Itivuttakapāḷi',
            'pdf_filename': 'Itivuttakapāḷi.pdf',
            'id_prefix': 'iti',
        },
        {
            'name': 'Suttanipātapāḷi',
            'pali_title': 'Suttanipātapāḷi',
            'pdf_filename': 'Suttanipātapāḷi.pdf',
            'id_prefix': 'snp',
        },
        {
            'name': 'Vimānavatthupāḷi',
            'pali_title': 'Vimānavatthupāḷi',
            'pdf_filename': 'Vimānavatthupāḷi.pdf',
            'id_prefix': 'vv',
        },
        {
            'name': 'Petavatthupāḷi',
            'pali_title': 'Petavatthupāḷi',
            'pdf_filename': 'Petavatthupāḷi.pdf',
            'id_prefix': 'pv',
        },
        {
            'name': 'Theragāthāpāḷi',
            'pali_title': 'Theragāthāpāḷi',
            'pdf_filename': 'Theragāthāpāḷi.pdf',
            'id_prefix': 'thag',
        },
        {
            'name': 'Therīgāthāpāḷi',
            'pali_title': 'Therīgāthāpāḷi',
            'pdf_filename': 'Therīgāthāpāḷi.pdf',
            'id_prefix': 'thig',
        },
        {
            'name': 'Jātakapāḷi_1',
            'pali_title': 'Jātakapāḷi 1',
            'pdf_filename': 'Jātakapāḷi_1.pdf',
            'id_prefix': 'ja1',
        },
        {
            'name': 'Jātakapāḷi_2',
            'pali_title': 'Jātakapāḷi 2',
            'pdf_filename': 'Jātakapāḷi_2.pdf',
            'id_prefix': 'ja2',
        },
        {
            'name': 'Mahāniddesapāḷi',
            'pali_title': 'Mahāniddesapāḷi',
            'pdf_filename': 'Mahāniddesapāḷi.pdf',
            'id_prefix': 'mnd',
        },
        {
            'name': 'Cūḷaniddesapāḷi',
            'pali_title': 'Cūḷaniddesapāḷi',
            'pdf_filename': 'Cūḷaniddesapāḷi.pdf',
            'id_prefix': 'cnd',
        },
        {
            'name': 'Paṭisambhidāmaggapāḷi',
            'pali_title': 'Paṭisambhidāmaggapāḷi',
            'pdf_filename': 'Paṭisambhidāmaggapāḷi.pdf',
            'id_prefix': 'ps',
        },
        {
            'name': 'Therāpadānapāḷi_1',
            'pali_title': 'Therāpadānapāḷi 1',
            'pdf_filename': 'Therāpadānapāḷi_1.pdf',
            'id_prefix': 'ap1',
        },
        {
            'name': 'Therāpadānapāḷi_2',
            'pali_title': 'Therāpadānapāḷi 2',
            'pdf_filename': 'Therāpadānapāḷi_2.pdf',
            'id_prefix': 'ap2',
        },
        {
            'name': 'Buddhavaṃsapāḷi',
            'pali_title': 'Buddhavaṃsapāḷi',
            'pdf_filename': 'Buddhavaṃsapāḷi.pdf',
            'id_prefix': 'bv',
        },
        {
            'name': 'Cariyāpiṭakapāḷi',
            'pali_title': 'Cariyāpiṭakapāḷi',
            'pdf_filename': 'Cariyāpiṭakapāḷi.pdf',
            'id_prefix': 'cp',
        },
        {
            'name': 'Nettippakaraṇapāḷi',
            'pali_title': 'Nettippakaraṇapāḷi',
            'pdf_filename': 'Nettippakaraṇapāḷi.pdf',
            'id_prefix': 'ne',
        },
        {
            'name': 'Peṭakopadesapāḷi',
            'pali_title': 'Peṭakopadesapāḷi',
            'pdf_filename': 'Peṭakopadesapāḷi.pdf',
            'id_prefix': 'pe',
        },
        {
            'name': 'Milindapañhapāḷi',
            'pali_title': 'Milindapañhapāḷi',
            'pdf_filename': 'Milindapañhapāḷi.pdf',
            'id_prefix': 'mil',
        }
    ]
    
    base_pdf_dir = r"Khuddakanikāye\pdfs"
    base_output_dir = r"Khuddakanikāye"
    
    # Verify base directories exist
    if not os.path.exists(base_pdf_dir):
        print(f"❌ Error: PDF directory not found: {base_pdf_dir}")
        return
    
    print("=" * 80)
    print("KHUDDAKA NIKĀYA BATCH EXTRACTION")
    print("=" * 80)
    print(f"\nProcessing {len(books)} Khuddaka PDFs...")
    print(f"PDF directory: {base_pdf_dir}")
    print(f"Output directory: {base_output_dir}\n")
    
    successful = 0
    failed = 0
    skipped = 0
    
    for i, book_info in enumerate(books, 1):
        print("\n" + "=" * 80)
        print(f"[{i}/{len(books)}] {book_info['name']}")
        print("=" * 80)
        
        # Skip Buddhavaṃsapāḷi (manually fixed by user)
        if book_info['name'] == 'Buddhavaṃsapāḷi':
            print(f"⚠️  Skipping: Buddhavaṃsapāḷi (manually fixed)")
            skipped += 1
            continue
        
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
            'id_prefix': book_info['id_prefix'],
            'use_generic_chapters': False,
        }
        
        try:
            # Create extractor and process
            extractor = KhuddakaExtractor(pdf_path, output_dir, book_config)
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

