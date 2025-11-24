"""
Fix and Re-translate Specific Chapters

This script re-translates chapters that have corrupted title/section translations
while preserving the original Pali text exactly as extracted.

Usage:
    python fix_and_retranslate.py dn2 dn4 dn5
    python fix_and_retranslate.py --all  # Re-translate all chapters
"""

import os
import json
import argparse
from translator import PaliTranslator, extract_chapter_from_text


def load_pali_source():
    """Load the original Pali source file"""
    pali_file = os.path.join("Pāthikavaggapāḷi", "Pāthikavaggapāḷi_pali_extracted.txt")
    with open(pali_file, 'r', encoding='utf-8') as f:
        return f.read()


def load_book_metadata():
    """Load the book.json metadata"""
    book_file = os.path.join("Pāthikavaggapāḷi", "book.json")
    with open(book_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def backup_chapter(chapter_file):
    """Create a backup of the existing chapter JSON"""
    if os.path.exists(chapter_file):
        backup_file = chapter_file + ".backup"
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [+] Created backup: {backup_file}")


def fix_chapter(chapter_id: str, translator: PaliTranslator, pali_text: str, book_data: dict):
    """
    Re-translate a specific chapter
    
    Args:
        chapter_id: Chapter ID like 'dn1', 'dn2', etc.
        translator: PaliTranslator instance
        pali_text: Full Pali source text
        book_data: Book metadata from book.json
    """
    print(f"\n{'='*60}")
    print(f"Re-translating Chapter: {chapter_id}")
    print(f"{'='*60}")
    
    # Find chapter info
    chapter_info = None
    for chapter in book_data.get('chapters', []):
        if chapter['id'] == chapter_id:
            chapter_info = chapter
            break
    
    if not chapter_info:
        print(f"[X] Chapter {chapter_id} not found in book.json")
        return False
    
    chapter_title_pali = chapter_info['title']['pali']
    print(f"Title: {chapter_title_pali}")
    
    # Find next chapter for boundary detection
    next_chapter_marker = None
    chapter_idx = book_data['chapters'].index(chapter_info)
    if chapter_idx < len(book_data['chapters']) - 1:
        next_chapter_marker = book_data['chapters'][chapter_idx + 1]['title']['pali']
    
    # Extract the chapter text
    print(f"Extracting chapter text...")
    chapter_text = extract_chapter_from_text(pali_text, chapter_title_pali, next_chapter_marker)
    
    if not chapter_text or len(chapter_text.strip()) < 100:
        print(f"[X] Failed to extract chapter text (too short or empty)")
        return False
    
    print(f"  [+] Extracted {len(chapter_text)} characters")
    
    # Backup existing file
    output_path = os.path.join("Pāthikavaggapāḷi", "chapters", f"{chapter_id}-{chapter_title_pali}.json")
    backup_chapter(output_path)
    
    # Translate the chapter
    print(f"\nStarting translation...")
    chapter_json = translator.translate_chapter(
        pali_text=chapter_text,
        chapter_id=chapter_id,
        chapter_title=chapter_title_pali
    )
    
    # Save the chapter
    translator.save_chapter_json(chapter_json, output_path)
    print(f"\n[+] Successfully re-translated and saved: {output_path}")
    
    return True


def main():
    # Fix Windows console encoding
    import sys
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    parser = argparse.ArgumentParser(description="Fix and re-translate specific chapters")
    parser.add_argument("chapters", nargs='*', help="Chapter IDs to re-translate (e.g., dn2 dn4 dn5)")
    parser.add_argument("--all", action="store_true", help="Re-translate all chapters")
    args = parser.parse_args()
    
    if not args.chapters and not args.all:
        print("[X] Please specify chapter IDs or use --all")
        print("\nUsage:")
        print("  python fix_and_retranslate.py dn2 dn4 dn5")
        print("  python fix_and_retranslate.py --all")
        return
    
    print("=== Fix and Re-translate Tool ===")
    print("=" * 60)
    
    # Load resources
    print("\n[*] Loading resources...")
    pali_text = load_pali_source()
    print(f"  [+] Loaded Pali source ({len(pali_text)} chars)")
    
    book_data = load_book_metadata()
    print(f"  [+] Loaded book metadata ({len(book_data['chapters'])} chapters)")
    
    # Initialize translator
    print("\n[*] Initializing translator...")
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("[X] GOOGLE_API_KEY environment variable not set!")
        return
    translator = PaliTranslator(api_key)
    print("  [+] Translator ready")
    
    # Determine which chapters to process
    if args.all:
        chapters_to_process = [ch['id'] for ch in book_data['chapters']]
        print(f"\n[!] Re-translating ALL {len(chapters_to_process)} chapters")
        response = input("Are you sure? This will take a long time. (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    else:
        chapters_to_process = args.chapters
    
    print(f"\n[*] Processing {len(chapters_to_process)} chapter(s)...")
    
    # Process each chapter
    success_count = 0
    failed_chapters = []
    
    for chapter_id in chapters_to_process:
        try:
            success = fix_chapter(chapter_id, translator, pali_text, book_data)
            if success:
                success_count += 1
            else:
                failed_chapters.append(chapter_id)
        except Exception as e:
            print(f"\n[X] Error processing {chapter_id}: {e}")
            failed_chapters.append(chapter_id)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"[+] Successfully re-translated: {success_count}/{len(chapters_to_process)} chapters")
    
    if failed_chapters:
        print(f"[X] Failed chapters: {', '.join(failed_chapters)}")
    else:
        print(f"[+] All chapters processed successfully!")
    
    print(f"\n[*] Backups were created with .backup extension")
    print(f"[*] Check translator.log for detailed progress")


if __name__ == "__main__":
    main()

