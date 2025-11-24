"""
Resume interrupted translation from where it left off
"""

import sys
import os
import json
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from translator import PaliTranslator, extract_chapter_from_text


def find_partial_translations(chapters_dir='Pāthikavaggapāḷi/chapters'):
    """
    Find partial translation files and determine resume point
    
    Returns:
        List of tuples: (chapter_id, completed_sections, total_sections, file_path)
    """
    partial_files = []
    
    if not os.path.exists(chapters_dir):
        return partial_files
    
    for filename in os.listdir(chapters_dir):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(chapters_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if it's marked as partial
            if data.get('_partial', False):
                chapter_id = data.get('id')
                completed = data.get('_completed_sections', 0)
                total = data.get('_total_sections', 0)
                
                partial_files.append((chapter_id, completed, total, filepath))
        except Exception as e:
            # Skip files that can't be read
            continue
    
    return partial_files


def find_last_attempted_chapter(log_file='translator.log'):
    """Find the last chapter that was being translated from log"""
    if not os.path.exists(log_file):
        return None
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Look for the last "Processing chapter" entry
        for line in reversed(lines[-100:]):
            if 'Processing chapter' in line:
                match = re.search(r'Processing chapter (dn\d+)', line)
                if match:
                    return match.group(1)
        
        return None
        
    except Exception as e:
        print(f"Error reading log: {e}")
        return None


def main():
    """Resume translation"""
    print("=" * 60)
    print("🔄 Resume Translation")
    print("=" * 60)
    
    # Check for partial translation files
    partial_files = find_partial_translations()
    
    # Also check log for last attempted chapter (in case no partial file exists yet)
    last_attempted = find_last_attempted_chapter()
    
    if not partial_files and not last_attempted:
        print("\n❌ No interrupted translations found")
        print("   No partial files or recent translation activity detected")
        print("\n💡 Use 'python translator.py' to start a new translation")
        return
    
    # Determine which chapter to resume
    current_chapter = None
    last_section = 0
    
    if partial_files:
        # Show partial files found
        print(f"\n📁 Found {len(partial_files)} partial translation(s):")
        for i, (ch_id, completed, total, filepath) in enumerate(partial_files, 1):
            print(f"   {i}. {ch_id}: {completed}/{total} sections completed")
        
        # Use the most recent one (or let user choose if multiple)
        if len(partial_files) == 1:
            current_chapter, last_section, _, _ = partial_files[0]
        else:
            choice = input(f"\nWhich chapter to resume? (1-{len(partial_files)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(partial_files):
                    current_chapter, last_section, _, _ = partial_files[idx]
                else:
                    print("Invalid choice")
                    return
            except ValueError:
                print("Invalid input")
                return
    else:
        # No partial files, but found attempted chapter in log
        current_chapter = last_attempted
        last_section = 0
        print(f"\n📖 Last attempted chapter: {current_chapter}")
        print(f"   No partial file found - will start from beginning")
    
    print(f"\n📖 Resuming:")
    print(f"   Chapter: {current_chapter}")
    print(f"   Last completed section: {last_section}")
    
    # Ask if want to resume
    response = input(f"\n❓ Resume from section {last_section + 1}? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Resume cancelled")
        return
    
    # Get API key
    api_key = input("\nEnter your Google Generative AI API key (or press Enter to use env variable): ").strip()
    
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY", "")
    
    if not api_key:
        print("\n❌ No API key provided")
        return
    
    # Initialize translator
    try:
        translator = PaliTranslator(api_key)
    except Exception as e:
        print(f"\n❌ Failed to initialize translator: {e}")
        return
    
    # Read the Pali text file
    pali_file = os.path.join("Pāthikavaggapāḷi", "Pāthikavaggapāḷi_pali_extracted.txt")
    
    try:
        with open(pali_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
    except Exception as e:
        print(f"\n❌ Failed to read Pali text file: {e}")
        return
    
    # Read book.json to get chapter information
    book_file = os.path.join("Pāthikavaggapāḷi", "book.json")
    
    try:
        with open(book_file, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
    except Exception as e:
        print(f"\n❌ Failed to read book.json: {e}")
        return
    
    # Find the chapter
    chapter = None
    for ch in book_data['chapters']:
        if ch['id'] == current_chapter:
            chapter = ch
            break
    
    if not chapter:
        print(f"\n❌ Could not find chapter {current_chapter} in book.json")
        return
    
    print(f"\n✓ Found chapter: {chapter['title']['pali']}")
    
    # Extract chapter text
    chapter_marker = chapter['title']['pali']
    chapter_idx = book_data['chapters'].index(chapter)
    next_marker = None
    if chapter_idx < len(book_data['chapters']) - 1:
        next_marker = book_data['chapters'][chapter_idx + 1]['title']['pali']
    
    chapter_text = extract_chapter_from_text(full_text, chapter_marker, next_marker)
    
    if not chapter_text:
        print(f"\n❌ Could not extract text for chapter {current_chapter}")
        return
    
    print(f"✓ Extracted {len(chapter_text)} characters")
    
    # Translate chapter (resuming from last section)
    print(f"\n🚀 Resuming translation from section {last_section + 1}...")
    print("=" * 60)
    
    try:
        output_path = os.path.join("Pāthikavaggapāḷi", "chapters", f"{chapter['id']}-{chapter['title']['pali']}.json")
        
        chapter_data = translator.translate_chapter(
            chapter_text,
            chapter['id'],
            chapter['title']['pali'],
            resume_from=last_section,
            output_path=output_path
        )
        
        # Save final version (without _partial markers)
        translator.save_chapter_json(chapter_data, output_path)
        
        print(f"\n✅ Chapter {chapter['id']} completed successfully!")
        print(f"   Saved to: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Error during translation: {e}")
        print(f"\n💡 Progress has been saved. You can try resuming again with:")
        print(f"   python resume_translation.py")


if __name__ == "__main__":
    main()

