"""
AI Translator Application for Pali Buddhist Texts
Handles rate limits, character limits, and creates structured JSON output
"""

import google.generativeai as genai
import json
import time
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# Import configuration
try:
    from config import (
        MODEL_NAME, RATE_LIMIT_DELAY, MAX_CHUNK_SIZE, MIN_SECTION_SIZE,
        MAX_SECTION_SIZE, TRANSLATION_TEMPERATURE, LOG_LEVEL, LOG_FILE,
        ENGLISH_TRANSLATION_INSTRUCTIONS, SINHALA_TRANSLATION_INSTRUCTIONS,
        REMOVE_PATTERNS, JSON_INDENT, JSON_ENSURE_ASCII
    )
except ImportError:
    # Fallback to defaults if config not found
    MODEL_NAME = 'gemini-1.5-flash'
    MAX_CHUNK_SIZE = 4000
    RATE_LIMIT_DELAY = 2
    MIN_SECTION_SIZE = 100
    MAX_SECTION_SIZE = 4000
    TRANSLATION_TEMPERATURE = 0.3
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'translator.log'
    ENGLISH_TRANSLATION_INSTRUCTIONS = ""
    SINHALA_TRANSLATION_INSTRUCTIONS = ""
    REMOVE_PATTERNS = []
    JSON_INDENT = 2
    JSON_ENSURE_ASCII = False

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


class PaliTranslator:
    """Translates Pali Buddhist texts to English and Sinhala"""
    
    def __init__(self, api_key: str):
        """Initialize the translator with Google Generative AI"""
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY", "")
        
        if not api_key:
            raise ValueError("API key is required. Set API_KEY or GOOGLE_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Translator initialized successfully with model: {MODEL_NAME}")
    
    def clean_translation(self, text: str) -> str:
        """
        Clean translation output:
        - Remove page numbers (Page X sur Y)
        - Remove prefixes like "Translation:", "Here is"
        - Remove Pali references in parentheses
        - Keep only the clean translation
        """
        # Use patterns from config if available
        patterns = REMOVE_PATTERNS if REMOVE_PATTERNS else [
            r'Page\s+\d+\s+(?:sur|of)\s+\d+',
            r'^Here is the translation[:\s]*',
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
    
    def translate_text(self, pali_text: str, target_language: str) -> str:
        """
        Translate Pali text to target language using Google Generative AI
        
        Args:
            pali_text: The Pali text to translate
            target_language: Either 'English' or 'Sinhala'
        
        Returns:
            Translated text
        """
        if not pali_text.strip():
            return ""
        
        prompt = f"""You are an expert translator of Pali Buddhist texts with deep knowledge of Buddhist philosophy and terminology.

Translate the following Pali text to {target_language}.

CRITICAL REQUIREMENTS:
1. Output ONLY the {target_language} translation
2. NO introductions, explanations, or notes
3. NO source text in parentheses or brackets
4. NO page numbers or references
5. Complete all sentences properly
6. Use clear, accurate {target_language}
7. Preserve paragraph structure
8. For Sinhala: Use proper Sinhala script
9. For English: Use clear, modern English

Translation Requirements:
1. Preserve the exact doctrinal and philosophical meaning
2. Keep traditional Buddhist terminology accurate (e.g., dhamma, karma, nibbana, bhikkhu)
3. Use modern, accessible language that's easy to understand
4. Explain complex concepts in contemporary terms while maintaining accuracy
5. Use everyday vocabulary where possible, but keep key Buddhist terms
6. Preserve paragraph breaks and structure
7. Handle Pali Unicode characters correctly (especially for Sinhala script)
8. Provide the Pali term in parentheses on first occurrence of technical terms
9. IMPORTANT: Complete ALL sentences - do not truncate or leave incomplete
10. Ensure the translation flows naturally and is grammatically complete

Pali Text:
{pali_text}

{target_language} Translation:"""
        
        try:
            logger.info(f"Translating {len(pali_text)} characters to {target_language}")
            response = self.model.generate_content(prompt)
            translation = response.text
            
            # Clean the translation
            translation = self.clean_translation(translation)
            
            logger.info(f"Translation completed: {len(translation)} characters")
            time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
            
            return translation
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            raise
    
    def split_into_sections(self, text: str) -> List[Dict[str, any]]:
        """
        Split Pali text into logical sections based on structure
        
        Returns:
            List of sections with metadata
        """
        sections = []
        lines = text.split('\n')
        
        current_section = {
            'number': 0,
            'pali': '',
            'title': '',
            'type': 'content'
        }
        
        section_num = 0
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Check if it's a title line (short line, often ends with specific patterns)
            is_title = False
            if len(line) < 100:
                # Check for title patterns
                if (line.endswith('suttaṃ') or 
                    line.endswith('vatthu') or 
                    line.endswith('kathā') or
                    re.match(r'^\d+\.\s+[A-Z]', line)):
                    is_title = True
            
            # Check if it's a new section (starts with number)
            if re.match(r'^\d+\.', line):
                # Save previous section if it has content
                if current_section['pali'].strip():
                    sections.append(current_section.copy())
                
                # Start new section
                section_num += 1
                current_section = {
                    'number': section_num,
                    'pali': line + '\n',
                    'title': '',
                    'type': 'content'
                }
            elif is_title:
                # If we have accumulated content, save it
                if current_section['pali'].strip():
                    sections.append(current_section.copy())
                
                # Start new titled section
                section_num += 1
                current_section = {
                    'number': section_num,
                    'pali': '',
                    'title': line,
                    'type': 'title'
                }
            else:
                # Add to current section
                current_section['pali'] += line + '\n'
        
        # Add final section
        if current_section['pali'].strip() or current_section['title']:
            sections.append(current_section)
        
        return sections
    
    def combine_small_sections(self, sections: List[Dict]) -> List[Dict]:
        """
        Combine small sections to optimize API calls
        Sections under MIN_SECTION_SIZE chars are combined with neighbors
        """
        if not sections:
            return []
        
        combined = []
        buffer = None
        
        for section in sections:
            pali_length = len(section.get('pali', ''))
            
            # If section is too small, add to buffer
            if pali_length < MIN_SECTION_SIZE and section['type'] != 'title':
                if buffer is None:
                    buffer = section.copy()
                else:
                    buffer['pali'] += '\n' + section['pali']
            else:
                # Flush buffer if exists
                if buffer:
                    combined.append(buffer)
                    buffer = None
                
                # Add current section
                combined.append(section)
        
        # Flush remaining buffer
        if buffer:
            combined.append(buffer)
        
        return combined
    
    def split_large_section(self, section: Dict) -> List[Dict]:
        """
        Split sections larger than MAX_CHUNK_SIZE into smaller chunks
        """
        pali_text = section.get('pali', '')
        
        if len(pali_text) <= MAX_CHUNK_SIZE:
            return [section]
        
        # Split by paragraphs
        paragraphs = pali_text.split('\n\n')
        chunks = []
        current_chunk = {
            'number': section['number'],
            'pali': '',
            'title': section.get('title', ''),
            'type': section['type']
        }
        
        for para in paragraphs:
            if len(current_chunk['pali']) + len(para) + 2 > MAX_CHUNK_SIZE:
                if current_chunk['pali']:
                    chunks.append(current_chunk.copy())
                current_chunk['pali'] = para + '\n\n'
            else:
                current_chunk['pali'] += para + '\n\n'
        
        if current_chunk['pali']:
            chunks.append(current_chunk)
        
        return chunks
    
    def process_sections(self, sections: List[Dict]) -> List[Dict]:
        """
        Process sections: combine small ones, split large ones
        """
        # First combine small sections
        sections = self.combine_small_sections(sections)
        
        # Then split large sections
        processed = []
        for section in sections:
            processed.extend(self.split_large_section(section))
        
        return processed
    
    def translate_chapter(self, pali_text: str, chapter_id: str, chapter_title: str) -> Dict:
        """
        Translate an entire chapter from Pali to English and Sinhala
        
        Args:
            pali_text: The full Pali text of the chapter
            chapter_id: ID like 'dn1'
            chapter_title: Pali title of the chapter
        
        Returns:
            Complete chapter JSON structure
        """
        logger.info(f"Processing chapter {chapter_id}: {chapter_title}")
        
        # Split into sections
        sections = self.split_into_sections(pali_text)
        logger.info(f"Found {len(sections)} initial sections")
        
        # Process sections (combine/split as needed)
        sections = self.process_sections(sections)
        logger.info(f"Processed to {len(sections)} optimized sections")
        
        # Translate each section
        translated_sections = []
        
        for i, section in enumerate(sections, 1):
            logger.info(f"Translating section {i}/{len(sections)}")
            
            pali_text = section.get('pali', '').strip()
            title = section.get('title', '').strip()
            
            if not pali_text and not title:
                continue
            
            # Translate the content
            if pali_text:
                english = self.translate_text(pali_text, 'English')
                sinhala = self.translate_text(pali_text, 'Sinhala')
            else:
                english = ""
                sinhala = ""
            
            # Translate title if exists
            if title:
                english_title = self.translate_text(title, 'English')
                sinhala_title = self.translate_text(title, 'Sinhala')
                
                # If this is a title-only section, put translation in title field
                if not pali_text:
                    pali_text = title
                    english = english_title
                    sinhala = sinhala_title
                else:
                    # Prepend title to content
                    pali_text = title + '\n\n' + pali_text
                    english = english_title + '\n\n' + english
                    sinhala = sinhala_title + '\n\n' + sinhala
            
            translated_section = {
                'number': section['number'],
                'pali': pali_text,
                'english': english,
                'sinhala': sinhala
            }
            
            translated_sections.append(translated_section)
        
        # Create chapter JSON structure
        chapter_json = {
            'id': chapter_id,
            'title': {
                'pali': chapter_title,
                'english': self.translate_text(chapter_title, 'English'),
                'sinhala': self.translate_text(chapter_title, 'Sinhala')
            },
            'sections': translated_sections
        }
        
        logger.info(f"Chapter {chapter_id} translation completed")
        return chapter_json
    
    def save_chapter_json(self, chapter_data: Dict, output_path: str):
        """Save chapter data to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(
                chapter_data, 
                f, 
                ensure_ascii=JSON_ENSURE_ASCII, 
                indent=JSON_INDENT
            )
        
        logger.info(f"Saved chapter to {output_path}")


def extract_chapter_from_text(text: str, chapter_marker: str, next_chapter_marker: str = None) -> str:
    """
    Extract a specific chapter from the full text
    
    Args:
        text: Full Pali text
        chapter_marker: Start marker (e.g., "1. Pāthikasuttaṃ")
        next_chapter_marker: End marker (next chapter title), None for last chapter
    
    Returns:
        Extracted chapter text
    """
    lines = text.split('\n')
    
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if chapter_marker in line:
            start_idx = i
        elif next_chapter_marker and next_chapter_marker in line and start_idx is not None:
            end_idx = i
            break
    
    if start_idx is None:
        return ""
    
    if end_idx is None:
        chapter_lines = lines[start_idx:]
    else:
        chapter_lines = lines[start_idx:end_idx]
    
    return '\n'.join(chapter_lines)


def main():
    """Main execution function"""
    print("=" * 60)
    print("Pali Buddhist Text Translator")
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
        translator = PaliTranslator(api_key)
    except Exception as e:
        print(f"ERROR: Failed to initialize translator: {e}")
        return
    
    # Read the Pali text file
    pali_file = "Pāthikavaggapāḷi/Pāthikavaggapāḷi_pali_extracted.txt"
    
    try:
        with open(pali_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
        print(f"✓ Loaded Pali text: {len(full_text)} characters")
    except Exception as e:
        print(f"ERROR: Failed to read Pali text file: {e}")
        return
    
    # Read book.json to get chapter information
    book_file = "Pāthikavaggapāḷi/book.json"
    
    try:
        with open(book_file, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
        print(f"✓ Loaded book metadata: {book_data['totalChapters']} chapters")
    except Exception as e:
        print(f"ERROR: Failed to read book.json: {e}")
        return
    
    # Process each chapter
    print("\n" + "=" * 60)
    print("Starting translation process...")
    print("=" * 60 + "\n")
    
    chapters = book_data['chapters']
    
    # Ask which chapters to process
    print(f"\nAvailable chapters:")
    for i, ch in enumerate(chapters, 1):
        print(f"{i}. {ch['id']} - {ch['title']['pali']}")
    
    choice = input("\nEnter chapter number to translate (or 'all' for all chapters): ").strip().lower()
    
    if choice == 'all':
        chapters_to_process = chapters
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(chapters):
                chapters_to_process = [chapters[idx]]
            else:
                print("Invalid chapter number")
                return
        except ValueError:
            print("Invalid input")
            return
    
    # Process selected chapters
    for i, chapter in enumerate(chapters_to_process):
        print(f"\n{'='*60}")
        print(f"Processing Chapter {i+1}/{len(chapters_to_process)}")
        print(f"ID: {chapter['id']}")
        print(f"Title: {chapter['title']['pali']}")
        print(f"{'='*60}\n")
        
        # Extract chapter text
        # Find chapter markers
        chapter_marker = chapter['title']['pali']
        
        # Find next chapter marker if not last
        next_marker = None
        chapter_idx = chapters.index(chapter)
        if chapter_idx < len(chapters) - 1:
            next_marker = chapters[chapter_idx + 1]['title']['pali']
        
        chapter_text = extract_chapter_from_text(full_text, chapter_marker, next_marker)
        
        if not chapter_text:
            print(f"WARNING: Could not extract text for chapter {chapter['id']}")
            continue
        
        print(f"Extracted {len(chapter_text)} characters")
        
        # Translate chapter
        try:
            chapter_data = translator.translate_chapter(
                chapter_text,
                chapter['id'],
                chapter['title']['pali']
            )
            
            # Save to file
            output_path = f"Pāthikavaggapāḷi/chapters/{chapter['id']}-{chapter['title']['pali']}.json"
            translator.save_chapter_json(chapter_data, output_path)
            
            print(f"✓ Chapter {chapter['id']} completed successfully!")
            
        except Exception as e:
            print(f"ERROR processing chapter {chapter['id']}: {e}")
            logger.exception("Detailed error:")
            continue
    
    print("\n" + "=" * 60)
    print("Translation process completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

