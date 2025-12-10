"""
Translate Section Titles and Footer in JSON Chapter Files
Adds missing English and Sinhala translations for paliTitle and footer fields
"""

import google.generativeai as genai
import json
import time
import os
import glob
import re
from pathlib import Path
from typing import Dict, List
import logging

# Import configuration
try:
    from config import (
        MODEL_NAME, RATE_LIMIT_DELAY, TRANSLATION_TEMPERATURE, 
        LOG_LEVEL, LOG_FILE, JSON_INDENT, JSON_ENSURE_ASCII,
        MAX_RETRIES, RETRY_DELAY, SERVER_OVERLOAD_RETRY_DELAY, API_TIMEOUT
    )
except ImportError:
    MODEL_NAME = 'gemini-2.0-flash'
    RATE_LIMIT_DELAY = 3.0
    TRANSLATION_TEMPERATURE = 0.3
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'translator.log'
    JSON_INDENT = 2
    JSON_ENSURE_ASCII = False
    MAX_RETRIES = 5
    RETRY_DELAY = 5
    SERVER_OVERLOAD_RETRY_DELAY = 30
    API_TIMEOUT = 120

# Setup logging
log_config = {
    'level': getattr(logging, LOG_LEVEL),
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}
if LOG_FILE:
    log_config['filename'] = LOG_FILE
    log_config['filemode'] = 'a'

logging.basicConfig(**log_config)
logger = logging.getLogger(__name__)


class TitleTranslator:
    """Translates paliTitle and footer fields in JSON chapter files"""
    
    def __init__(self, api_key: str):
        """Initialize the translator with Google Generative AI"""
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY", "")
        
        if not api_key:
            raise ValueError("API key is required. Set API_KEY or GOOGLE_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Title Translator initialized with model: {MODEL_NAME}")
    
    def validate_sinhala_characters(self, text: str) -> tuple:
        """Validate that Sinhala text doesn't contain foreign script characters"""
        TAMIL_RANGE = r'\u0B80-\u0BFF'
        BENGALI_RANGE = r'\u0980-\u09FF'
        DEVANAGARI_RANGE = r'\u0900-\u097F'
        TELUGU_RANGE = r'\u0C00-\u0C7F'
        KANNADA_RANGE = r'\u0C80-\u0CFF'
        MALAYALAM_RANGE = r'\u0D00-\u0D7F'
        THAI_RANGE = r'\u0E00-\u0E7F'
        BURMESE_RANGE = r'\u1000-\u109F'
        KHMER_RANGE = r'\u1780-\u17FF'
        
        foreign_pattern = re.compile(
            f'[{TAMIL_RANGE}{BENGALI_RANGE}{DEVANAGARI_RANGE}{TELUGU_RANGE}'
            f'{KANNADA_RANGE}{MALAYALAM_RANGE}{THAI_RANGE}{BURMESE_RANGE}{KHMER_RANGE}]'
        )
        
        script_patterns = {
            'Tamil': re.compile(f'[{TAMIL_RANGE}]'),
            'Bengali': re.compile(f'[{BENGALI_RANGE}]'),
            'Hindi/Devanagari': re.compile(f'[{DEVANAGARI_RANGE}]'),
            'Telugu': re.compile(f'[{TELUGU_RANGE}]'),
            'Kannada': re.compile(f'[{KANNADA_RANGE}]'),
            'Malayalam': re.compile(f'[{MALAYALAM_RANGE}]'),
            'Thai': re.compile(f'[{THAI_RANGE}]'),
            'Burmese': re.compile(f'[{BURMESE_RANGE}]'),
            'Khmer': re.compile(f'[{KHMER_RANGE}]'),
        }
        
        issues = []
        for match in foreign_pattern.finditer(text):
            char = match.group()
            position = match.start()
            
            script = "Unknown"
            for script_name, pattern in script_patterns.items():
                if pattern.match(char):
                    script = script_name
                    break
            
            start = max(0, position - 20)
            end = min(len(text), position + 20)
            context = text[start:end]
            
            issues.append({
                'char': char,
                'unicode': f'U+{ord(char):04X}',
                'script': script,
                'position': position,
                'context': context
            })
        
        return len(issues) == 0, issues
    
    def clean_translation(self, text: str) -> str:
        """Clean translation output"""
        patterns = [
            r'Page\s+\d+\s+(?:sur|of)\s+\d+',
            r'^Here is the translation[:\s]*',
            r'^Here\'s the translation[:\s]*',
            r'^Translation[:\s]*',
            r'^සිංහල පරිවර්තනය[:\s]*',
            r'^English translation[:\s]*',
            r'^Sinhala translation[:\s]*',
            r'^\*+\s*Translation\s*\*+[:\s]*',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = text.strip()
        
        return text
    
    def translate_title(self, pali_title: str, target_language: str, retry_count: int = 0) -> str:
        """Translate a Pali title to target language"""
        if not pali_title.strip():
            return ""
        
        prompt = f"""You are an expert translator of Pali Buddhist texts.

Translate this Pali section title to {target_language}.

REQUIREMENTS:
1. Output ONLY the {target_language} translation
2. Keep it SHORT and concise (max 10 words)
3. NO explanations or notes
4. Use proper {target_language} script
5. Preserve the meaning accurately
6. For numerical titles (Tikaṃ, Sattakaṃ, Aṭṭhakaṃ), translate the NUMBER meaning

CRITICAL FOR SINHALA:
- PRESERVE Zero-Width Joiner (U+200D) for proper rendering
- Use ONLY Sinhala Unicode (U+0D80-U+0DFF)
- NO Tamil, Hindi, Thai, or other foreign scripts
- Conjuncts MUST have ZWJ: භාග්‍යවතුන්, ශ්‍රවණ, ධර්මය, ත්‍රිකය, සප්තකය, අෂ්ටකය

EXAMPLES:
- "Tikaṃ" → English: "The Triad" / Sinhala: "ත්‍රිකය" (means "group of three")
- "Sattakaṃ" → English: "The Heptad" / Sinhala: "සප්තකය" (means "group of seven")
- "Aṭṭhakaṃ" → English: "The Octad" / Sinhala: "අෂ්ටකය" (means "group of eight")
- "Korakkhattiyavatthu" → English: "Story of Korakkhattiya" / Sinhala: "කෝරක්ඛත්තිය වස්තුව"

Pali Title: {pali_title}

{target_language} Translation:"""
        
        try:
            logger.info(f"Translating title '{pali_title}' to {target_language}")
            
            response = self.model.generate_content(
                prompt,
                request_options={"timeout": API_TIMEOUT}
            )
            
            if not response.text or not response.text.strip():
                raise ValueError("Empty response from API")
            
            translation = response.text.strip()
            translation = self.clean_translation(translation)
            
            # Validate Sinhala characters
            if target_language == 'Sinhala':
                is_valid, issues = self.validate_sinhala_characters(translation)
                if not is_valid:
                    logger.warning(f"Foreign characters detected in Sinhala title: {len(issues)} issues")
                    for issue in issues[:3]:
                        logger.warning(f"  {issue['script']} char '{issue['char']}' ({issue['unicode']}) at position {issue['position']}")
                    
                    # Try to fix foreign characters
                    fix_prompt = f"""The following Sinhala text contains FOREIGN script characters.
Please rewrite it using ONLY proper Sinhala Unicode characters (U+0D80-U+0DFF).

PROBLEMATIC TEXT:
{translation}

ISSUES FOUND:
{chr(10).join([f"- {issue['script']} character '{issue['char']}' ({issue['unicode']})" for issue in issues[:5]])}

CORRECTED SINHALA TEXT (using ONLY Sinhala Unicode U+0D80-U+0DFF):"""
                    
                    try:
                        logger.info("Attempting to fix foreign characters in Sinhala title")
                        fix_response = self.model.generate_content(fix_prompt)
                        fixed_text = self.clean_translation(fix_response.text)
                        
                        # Validate again
                        is_valid_now, remaining_issues = self.validate_sinhala_characters(fixed_text)
                        if is_valid_now:
                            logger.info("Successfully corrected all foreign characters")
                            translation = fixed_text
                        else:
                            logger.warning(f"Still {len(remaining_issues)} foreign characters remain after fix attempt")
                            translation = fixed_text
                        
                        time.sleep(RATE_LIMIT_DELAY)
                    except Exception as fix_error:
                        logger.warning(f"Failed to fix foreign characters: {str(fix_error)}")
            
            logger.info(f"Title translation completed: {translation}")
            time.sleep(RATE_LIMIT_DELAY)
            
            return translation
            
        except Exception as e:
            error_str = str(e).lower()
            error_code = str(e)
            
            # Handle 503 Server Overload
            if '503' in error_code or 'overloaded' in error_str:
                if retry_count < MAX_RETRIES:
                    wait_time = SERVER_OVERLOAD_RETRY_DELAY * (retry_count + 1)
                    logger.warning(f"Server overload, waiting {wait_time}s (attempt {retry_count + 1}/{MAX_RETRIES})")
                    print(f"  ⚠ Server overloaded! Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    return self.translate_title(pali_title, target_language, retry_count + 1)
            
            # Handle rate limit errors
            if '429' in error_code or 'rate limit' in error_str:
                if retry_count < MAX_RETRIES:
                    wait_time = (2 ** retry_count) * RETRY_DELAY * 2
                    logger.warning(f"Rate limit hit, waiting {wait_time}s")
                    print(f"  ⚠ Rate limit! Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    return self.translate_title(pali_title, target_language, retry_count + 1)
            
            logger.error(f"Translation error: {str(e)}")
            raise
    
    def process_json_file(self, json_path: str, resume_from_section: int = 0) -> Dict:
        """
        Process a JSON chapter file and translate missing titles and footer
        
        Args:
            json_path: Path to the JSON file
            resume_from_section: Section index to resume from (0 = start from beginning)
        
        Returns:
            Updated chapter data with statistics
        """
        logger.info(f"Processing file: {json_path}")
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(json_path)}")
        print(f"{'='*60}\n")
        
        # Load JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data.get('id', 'unknown')
        sections = chapter_data.get('sections', [])
        
        stats = {
            'titles_translated': 0,
            'titles_skipped': 0,
            'vaggas_translated': 0,
            'footer_translated': False
        }
        
        # Resume logic
        if resume_from_section > 0:
            print(f"🔄 RESUMING from section {resume_from_section + 1}/{len(sections)}\n")
            logger.info(f"Resuming from section {resume_from_section + 1}")
        
        # Process section titles
        for i, section in enumerate(sections):
            # Skip sections before resume point
            if i < resume_from_section:
                continue
            
            pali_title = section.get('paliTitle', '').strip()
            
            if not pali_title:
                continue
            
            section_num = section.get('number', i+1)
            has_english = section.get('englishTitle', '').strip()
            has_sinhala = section.get('sinhalaTitle', '').strip()
            
            # Check for vagga field
            vagga = section.get('vagga', '').strip()
            has_vagga_english = section.get('vaggaEnglish', '').strip()
            has_vagga_sinhala = section.get('vaggaSinhala', '').strip()
            
            # Skip if all translations exist
            if has_english and has_sinhala and (not vagga or (has_vagga_english and has_vagga_sinhala)):
                stats['titles_skipped'] += 1
                continue
            
            print(f"[{i+1}/{len(sections)}] Section {section_num}: {pali_title}")
            
            try:
                # Translate to English if missing
                if not has_english:
                    print(f"  → English title...", end='', flush=True)
                    english_title = self.translate_title(pali_title, 'English')
                    section['englishTitle'] = english_title
                    print(f" ✓ {english_title}")
                else:
                    print(f"  ✓ English: {has_english}")
                
                # Translate to Sinhala if missing
                if not has_sinhala:
                    print(f"  → Sinhala title...", end='', flush=True)
                    sinhala_title = self.translate_title(pali_title, 'Sinhala')
                    section['sinhalaTitle'] = sinhala_title
                    print(f" ✓ {sinhala_title}")
                else:
                    print(f"  ✓ Sinhala: {has_sinhala}")
                
                # Translate vagga if present and missing translations
                if vagga:
                    if not has_vagga_english:
                        print(f"  → English vagga ({vagga})...", end='', flush=True)
                        english_vagga = self.translate_title(vagga, 'English')
                        section['vaggaEnglish'] = english_vagga
                        print(f" ✓ {english_vagga}")
                    else:
                        print(f"  ✓ Vagga English: {has_vagga_english}")
                    
                    if not has_vagga_sinhala:
                        print(f"  → Sinhala vagga ({vagga})...", end='', flush=True)
                        sinhala_vagga = self.translate_title(vagga, 'Sinhala')
                        section['vaggaSinhala'] = sinhala_vagga
                        print(f" ✓ {sinhala_vagga}")
                    else:
                        print(f"  ✓ Vagga Sinhala: {has_vagga_sinhala}")
                    
                    if not has_vagga_english or not has_vagga_sinhala:
                        stats['vaggas_translated'] += 1
                
                stats['titles_translated'] += 1
                
                # Save progress after each section
                try:
                    temp_path = json_path + '.partial'
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(chapter_data, f, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT)
                    os.replace(temp_path, json_path)
                    logger.info(f"Saved progress for section {section_num}")
                except Exception as e:
                    logger.warning(f"Failed to save progress: {e}")
            
            except Exception as e:
                error_str = str(e).lower()
                logger.error(f"Error translating section {i+1}: {str(e)}")
                print(f"\n❌ ERROR at section {i+1}: {str(e)}")
                
                # Check if it's a quota/rate limit error
                if 'quota' in error_str or 'rate limit' in error_str or '429' in str(e):
                    print(f"\n⛔ QUOTA EXCEEDED - Translation stopped at section {i+1}/{len(sections)}")
                    logger.error(f"Quota exceeded at section {i+1}")
                    print(f"\n💡 To resume later, use: resume_from_section={i}")
                    raise Exception(f"Quota exceeded at section {i+1}. Resume with: resume_from_section={i}")
                
                # For other errors, save progress and continue
                print(f"⚠ Skipping section {i+1} due to error")
                continue
        
        # Process footer
        footer = chapter_data.get('footer', {})
        if footer:
            pali_footer = footer.get('pali', '').strip()
            
            if pali_footer:
                has_english_footer = footer.get('english', '').strip()
                has_sinhala_footer = footer.get('sinhala', '').strip()
                
                if not has_english_footer or not has_sinhala_footer:
                    print(f"\n📄 Footer: {pali_footer}")
                    
                    if not has_english_footer:
                        print(f"  → English footer...", end='', flush=True)
                        english_footer = self.translate_title(pali_footer, 'English')
                        footer['english'] = english_footer
                        print(f" ✓ {english_footer}")
                    
                    if not has_sinhala_footer:
                        print(f"  → Sinhala footer...", end='', flush=True)
                        sinhala_footer = self.translate_title(pali_footer, 'Sinhala')
                        footer['sinhala'] = sinhala_footer
                        print(f" ✓ {sinhala_footer}")
                    
                    chapter_data['footer'] = footer
                    stats['footer_translated'] = True
        
        # Final save
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(chapter_data, f, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT)
        
        logger.info(f"Chapter {chapter_id} completed: {stats['titles_translated']} titles translated, {stats['vaggas_translated']} vaggas translated, {stats['titles_skipped']} skipped")
        print(f"\n✅ Completed: {stats['titles_translated']} titles translated, {stats['vaggas_translated']} vaggas translated, {stats['titles_skipped']} already done")
        
        return stats
    
    def process_directory(self, directory: str, file_pattern: str = "*.json", resume_from_file: str = None, resume_from_section: int = 0, recursive: bool = False):
        """
        Process all JSON files in a directory
        
        Args:
            directory: Base directory to search
            file_pattern: File pattern to match (e.g., "*.json", "mn*.json")
            resume_from_file: Filename to resume from
            resume_from_section: Section index to resume from
            recursive: If True, search all subdirectories for 'chapters' folders
        """
        json_files = []
        
        if recursive:
            # Find all 'chapters' subdirectories recursively
            print(f"\n🔍 Searching for 'chapters' directories in: {directory}")
            chapters_dirs = []
            
            for root, dirs, files in os.walk(directory):
                if 'chapters' in dirs:
                    chapters_path = os.path.join(root, 'chapters')
                    chapters_dirs.append(chapters_path)
            
            if not chapters_dirs:
                print(f"No 'chapters' directories found in {directory}")
                return
            
            print(f"Found {len(chapters_dirs)} chapters directories:")
            for chapters_dir in sorted(chapters_dirs):
                rel_path = os.path.relpath(chapters_dir, directory)
                print(f"  📁 {rel_path}")
            
            # Collect all JSON files from all chapters directories
            for chapters_dir in sorted(chapters_dirs):
                matching_files = sorted(glob.glob(os.path.join(chapters_dir, file_pattern)))
                json_files.extend(matching_files)
                if matching_files:
                    rel_path = os.path.relpath(chapters_dir, directory)
                    print(f"  ✓ {len(matching_files)} files in {rel_path}")
        else:
            # Single directory mode (original behavior)
            json_files = sorted(glob.glob(os.path.join(directory, file_pattern)))
        
        if not json_files:
            print(f"No JSON files found matching pattern '{file_pattern}'")
            return
        
        print(f"\n📚 Total: {len(json_files)} JSON files to process")
        
        # If resuming, skip files before resume point
        start_index = 0
        if resume_from_file:
            for idx, json_file in enumerate(json_files):
                if os.path.basename(json_file) == resume_from_file:
                    start_index = idx
                    print(f"\n🔄 Resuming from file: {resume_from_file}")
                    break
            if start_index == 0 and resume_from_file:
                print(f"\n⚠ Warning: Resume file '{resume_from_file}' not found. Starting from beginning.")
        
        total_stats = {
            'files_processed': 0,
            'titles_translated': 0,
            'vaggas_translated': 0,
            'titles_skipped': 0,
            'footers_translated': 0
        }
        
        for idx, json_file in enumerate(json_files[start_index:], start=start_index):
            try:
                # Only resume from section on the first file
                section_resume = resume_from_section if idx == start_index else 0
                
                stats = self.process_json_file(json_file, resume_from_section=section_resume)
                total_stats['files_processed'] += 1
                total_stats['titles_translated'] += stats['titles_translated']
                total_stats['vaggas_translated'] += stats['vaggas_translated']
                total_stats['titles_skipped'] += stats['titles_skipped']
                if stats['footer_translated']:
                    total_stats['footers_translated'] += 1
            except Exception as e:
                error_str = str(e).lower()
                if 'quota' in error_str or 'rate limit' in error_str:
                    print(f"\n⛔ Stopping due to quota/rate limit")
                    print(f"💡 To resume, use:")
                    print(f"   resume_from_file='{os.path.basename(json_file)}'")
                    break
                else:
                    print(f"\n❌ Error processing {json_file}: {e}")
                    logger.exception(f"Error processing {json_file}")
                    continue
        
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Files processed: {total_stats['files_processed']}")
        print(f"Titles translated: {total_stats['titles_translated']}")
        print(f"Vaggas translated: {total_stats['vaggas_translated']}")
        print(f"Titles skipped: {total_stats['titles_skipped']}")
        print(f"Footers translated: {total_stats['footers_translated']}")
        print(f"{'='*60}")


def main():
    """Main execution function"""
    print("=" * 60)
    print("Section Title & Footer Translator")
    print("=" * 60)
    
    # Get API key
    api_key = input("Enter your Google Generative AI API key (or press Enter to use env variable): ").strip()
    
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY", "")
    
    if not api_key:
        print("ERROR: No API key provided. Set GOOGLE_API_KEY environment variable or enter it when prompted.")
        return
    
    # Initialize translator
    try:
        translator = TitleTranslator(api_key)
    except Exception as e:
        print(f"ERROR: Failed to initialize translator: {e}")
        return
    
    # Get directory path
    print("\nDirectory Options:")
    print("  1. Single chapters directory (e.g., Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters)")
    print("  2. Parent directory with multiple subdirectories (e.g., Majjhimanikāye)")
    
    directory = input("\nEnter directory path: ").strip()
    
    if not directory:
        directory = "Pāthikavaggapāḷi/chapters"
    
    if not os.path.exists(directory):
        print(f"ERROR: Directory not found: {directory}")
        return
    
    # Determine if recursive search is needed
    recursive = False
    has_chapters_subdir = os.path.exists(os.path.join(directory, 'chapters'))
    is_chapters_dir = os.path.basename(directory) == 'chapters'
    
    if not is_chapters_dir and not has_chapters_subdir:
        # Check if there are subdirectories with 'chapters' folders
        has_nested_chapters = False
        for root, dirs, files in os.walk(directory):
            if 'chapters' in dirs:
                has_nested_chapters = True
                break
        
        if has_nested_chapters:
            recursive_input = input("\nFound subdirectories with 'chapters' folders. Search recursively? (y/n, default: y): ").strip().lower()
            recursive = recursive_input != 'n'
        else:
            print("\nNo 'chapters' subdirectories found. Will search in the specified directory.")
    
    # Ask about file pattern
    file_pattern = input("\nEnter file pattern (default: *.json, examples: mn*.json, dn*.json): ").strip()
    if not file_pattern:
        file_pattern = "*.json"
    
    # Ask about resuming
    resume_from_file = input("\nResume from file (e.g., mn.3.1-Devadahavaggo.json) or press Enter to start from beginning: ").strip()
    resume_from_section = 0
    
    if resume_from_file:
        section_input = input("Resume from section number (press Enter for section 1): ").strip()
        if section_input:
            try:
                resume_from_section = int(section_input) - 1
                if resume_from_section < 0:
                    resume_from_section = 0
            except ValueError:
                print("Invalid section number, starting from section 1")
                resume_from_section = 0
    
    # Process directory
    try:
        translator.process_directory(
            directory, 
            file_pattern=file_pattern,
            resume_from_file=resume_from_file,
            resume_from_section=resume_from_section,
            recursive=recursive
        )
        print("\n✓ Translation process completed!")
    except Exception as e:
        print(f"\nERROR: {e}")
        logger.exception("Detailed error:")
        return


if __name__ == "__main__":
    main()
