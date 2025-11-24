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
        MODEL_NAME, VERIFY_MODEL_NAME, ENABLE_VERIFICATION, VERIFY_DELAY,
        RATE_LIMIT_DELAY, MAX_CHUNK_SIZE, MIN_SECTION_SIZE,
        MAX_SECTION_SIZE, TRANSLATION_TEMPERATURE, LOG_LEVEL, LOG_FILE,
        ENGLISH_TRANSLATION_INSTRUCTIONS, SINHALA_TRANSLATION_INSTRUCTIONS,
        VERIFICATION_INSTRUCTIONS, REMOVE_PATTERNS, JSON_INDENT, JSON_ENSURE_ASCII
    )
except ImportError:
    # Fallback to defaults if config not found
    MODEL_NAME = 'gemini-2.0-flash'
    VERIFY_MODEL_NAME = 'gemini-2.0-flash'
    ENABLE_VERIFICATION = False
    VERIFY_DELAY = 2
    MAX_CHUNK_SIZE = 4000
    RATE_LIMIT_DELAY = 2
    MIN_SECTION_SIZE = 100
    MAX_SECTION_SIZE = 4000
    TRANSLATION_TEMPERATURE = 0.3
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'translator.log'
    ENGLISH_TRANSLATION_INSTRUCTIONS = ""
    SINHALA_TRANSLATION_INSTRUCTIONS = ""
    VERIFICATION_INSTRUCTIONS = ""
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
    """Translates Pali Buddhist texts to English and Sinhala with optional verification"""
    
    def __init__(self, api_key: str):
        """Initialize the translator with Google Generative AI"""
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY", "")
        
        if not api_key:
            raise ValueError("API key is required. Set API_KEY or GOOGLE_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        
        # Primary translation model
        self.model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Primary translator initialized with model: {MODEL_NAME}")
        
        # Verification model (can be same or different)
        if ENABLE_VERIFICATION:
            self.verify_model = genai.GenerativeModel(VERIFY_MODEL_NAME)
            logger.info(f"Verification model initialized: {VERIFY_MODEL_NAME}")
        else:
            self.verify_model = None
            logger.info("Verification disabled")
    
    def validate_sinhala_characters(self, text: str) -> tuple[bool, list[dict]]:
        """
        Validate that Sinhala text doesn't contain foreign script characters.
        
        Args:
            text: The Sinhala text to validate
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        import re
        
        # Unicode ranges for different scripts
        TAMIL_RANGE = r'\u0B80-\u0BFF'
        BENGALI_RANGE = r'\u0980-\u09FF'
        DEVANAGARI_RANGE = r'\u0900-\u097F'  # Hindi
        TELUGU_RANGE = r'\u0C00-\u0C7F'
        KANNADA_RANGE = r'\u0C80-\u0CFF'
        MALAYALAM_RANGE = r'\u0D00-\u0D7F'
        THAI_RANGE = r'\u0E00-\u0E7F'
        BURMESE_RANGE = r'\u1000-\u109F'
        KHMER_RANGE = r'\u1780-\u17FF'
        
        # Pattern to detect foreign characters (including Southeast Asian scripts)
        foreign_pattern = re.compile(
            f'[{TAMIL_RANGE}{BENGALI_RANGE}{DEVANAGARI_RANGE}{TELUGU_RANGE}'
            f'{KANNADA_RANGE}{MALAYALAM_RANGE}{THAI_RANGE}{BURMESE_RANGE}{KHMER_RANGE}]'
        )
        
        # Script identification patterns
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
            
            # Identify script
            script = "Unknown"
            for script_name, pattern in script_patterns.items():
                if pattern.match(char):
                    script = script_name
                    break
            
            # Extract context
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
        """
        Clean translation output:
        - Remove page numbers (Page X sur Y)
        - Remove prefixes like "Translation:", "Here is"
        - Remove meta-instructions from AI
        - Remove Pali references in parentheses
        - Remove leading section numbers (e.g., "1.", "49.", "10 .")
        - Keep only the clean translation
        """
        # Use patterns from config if available
        patterns = REMOVE_PATTERNS if REMOVE_PATTERNS else [
            r'Page\s+\d+\s+(?:sur|of)\s+\d+',
            r'^Here is the translation[:\s]*',
            r'^Here\'s the translation[:\s]*',
            r'^Here is the corrected.*?text[:\s]*',
            r'^Here\'s the corrected.*?text[:\s]*',
            r'^Translation[:\s]*',
            r'^සිංහල පරිවර්තනය[:\s]*',
            r'^English translation[:\s]*',
            r'^Sinhala translation[:\s]*',
            r'^\*+\s*Translation\s*\*+[:\s]*',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # **CRITICAL**: Remove leading section numbers (e.g., "1. ", "49. ", "10 .")
        # This matches: start of line, optional whitespace, number(s), optional whitespace, period, whitespace
        text = re.sub(r'^\s*\d+\s*\.\s+', '', text, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = text.strip()
        
        return text
    
    def translate_text(self, pali_text: str, target_language: str, retry_count: int = 0, max_retries: int = 3) -> str:
        """
        Translate Pali text to target language using Google Generative AI
        
        Args:
            pali_text: The Pali text to translate
            target_language: Either 'English' or 'Sinhala'
            retry_count: Current retry attempt (internal use)
            max_retries: Maximum number of retries
        
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
8. For Sinhala: Use proper Sinhala script (U+0D80-U+0DFF) with Zero-Width Joiner (U+200D)
9. For English: Use clear, modern English

CRITICAL FOR SINHALA:
- PRESERVE Zero-Width Joiner (U+200D) for proper rendering: භාග්‍යවතුන්, ශ්‍රවණ, ධර්මය
- Use ONLY Sinhala Unicode (U+0D80-U+0DFF) - NO Tamil, Hindi, Thai, or other scripts
- Conjuncts MUST have ZWJ: ක්‍ය, ක්‍ර, ප්‍ර, ත්‍ර, ශ්‍ර, ග්‍ර

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
            
            # Check if response was blocked or empty
            if not response.text or not response.text.strip():
                # Check finish_reason
                if hasattr(response, 'candidates') and response.candidates:
                    finish_reason = response.candidates[0].finish_reason
                    logger.warning(f"Empty response with finish_reason: {finish_reason}")
                    
                    # finish_reason 8 typically means RECITATION (blocked due to recitation of copyrighted content)
                    # or other safety blocks
                    if finish_reason in [8, 4, 5]:  # RECITATION, SAFETY, OTHER
                        if retry_count < max_retries:
                            wait_time = (2 ** retry_count) * RATE_LIMIT_DELAY  # Exponential backoff
                            logger.info(f"Retrying after {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                            print(f"  ⚠ Response blocked (reason {finish_reason}), retrying in {wait_time}s...")
                            time.sleep(wait_time)
                            return self.translate_text(pali_text, target_language, retry_count + 1, max_retries)
                        else:
                            raise ValueError(f"Translation blocked by API after {max_retries} retries (finish_reason: {finish_reason})")
                
                raise ValueError("Empty response from API")
            
            translation = response.text
            
            # Clean the translation
            translation = self.clean_translation(translation)
            
            logger.info(f"Translation completed: {len(translation)} characters")
            time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
            
            return translation
            
        except ValueError as e:
            # Re-raise ValueError (our custom errors)
            logger.error(f"Translation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            
            # Check if it's a finish_reason error
            if "finish_reason" in str(e):
                if retry_count < max_retries:
                    wait_time = (2 ** retry_count) * RATE_LIMIT_DELAY  # Exponential backoff
                    logger.info(f"Retrying after {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                    print(f"  ⚠ API error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    return self.translate_text(pali_text, target_language, retry_count + 1, max_retries)
                else:
                    logger.error(f"Translation failed after {max_retries} retries")
            
            raise
    
    def verify_and_improve_translation(self, pali_text: str, translated_text: str, target_language: str) -> str:
        """
        Verify translation accuracy and improve readability using a second AI model
        
        Args:
            pali_text: Original Pali text
            translated_text: The translated text to verify
            target_language: Either 'English' or 'Sinhala'
        
        Returns:
            Verified and improved translation
        """
        if not ENABLE_VERIFICATION or not self.verify_model:
            return translated_text
        
        if not pali_text.strip() or not translated_text.strip():
            return translated_text
        
        # Format the verification prompt
        verification_prompt = VERIFICATION_INSTRUCTIONS.format(language=target_language)
        
        prompt = f"""{verification_prompt}

ORIGINAL PALI TEXT:
{pali_text}

CURRENT {target_language.upper()} TRANSLATION:
{translated_text}

YOUR TASK:
1. Verify the translation is accurate and complete (1-to-1 mapping with Pali)
2. Improve readability and make it more natural/modern while preserving exact meaning
3. Fix any errors or awkward phrasing
4. Return ONLY the improved {target_language} translation

IMPROVED {target_language.upper()} TRANSLATION:"""
        
        try:
            logger.info(f"Verifying {target_language} translation ({len(translated_text)} chars)")
            response = self.verify_model.generate_content(prompt)
            verified_text = response.text
            
            # Clean the verified translation
            verified_text = self.clean_translation(verified_text)
            
            # Validate Sinhala text for foreign characters
            if target_language == 'Sinhala':
                is_valid, issues = self.validate_sinhala_characters(verified_text)
                if not is_valid:
                    logger.warning(f"Foreign characters detected in Sinhala translation: {len(issues)} issues")
                    for issue in issues[:3]:  # Log first 3 issues
                        logger.warning(f"  {issue['script']} char '{issue['char']}' at position {issue['position']}")
                    
                    # Try to fix by asking AI to correct it
                    fix_prompt = f"""The following Sinhala text contains foreign script characters that need to be corrected.
Please rewrite it using ONLY proper Sinhala Unicode characters (U+0D80-U+0DFF).

PROBLEMATIC TEXT:
{verified_text}

ISSUES FOUND:
{chr(10).join([f"- {issue['script']} character '{issue['char']}' ({issue['unicode']}) in context: {issue['context']}" for issue in issues[:5]])}

Please provide the corrected Sinhala text with all foreign characters replaced with proper Sinhala equivalents:"""
                    
                    try:
                        fix_response = self.verify_model.generate_content(fix_prompt)
                        fixed_text = self.clean_translation(fix_response.text)
                        
                        # Validate again
                        is_valid_now, remaining_issues = self.validate_sinhala_characters(fixed_text)
                        if is_valid_now:
                            logger.info("Successfully corrected foreign characters")
                            verified_text = fixed_text
                        else:
                            logger.warning(f"Still {len(remaining_issues)} foreign characters after correction attempt")
                            # Use the fixed text anyway as it's likely better
                            verified_text = fixed_text
                        
                        time.sleep(VERIFY_DELAY)  # Additional delay for fix attempt
                    except Exception as fix_error:
                        logger.warning(f"Failed to fix foreign characters: {str(fix_error)}")
            
            # Log if significant changes were made
            if len(verified_text) != len(translated_text):
                logger.info(f"Verification adjusted length: {len(translated_text)} → {len(verified_text)} chars")
            else:
                logger.info(f"Verification completed (no length change)")
            
            time.sleep(VERIFY_DELAY)  # Rate limiting for verification
            
            return verified_text
            
        except Exception as e:
            logger.warning(f"Verification failed: {str(e)}. Using original translation.")
            # If verification fails, return the original translation
            return translated_text
    
    def split_into_sections(self, text: str) -> List[Dict[str, any]]:
        """
        Split Pali text into logical sections based on structure
        
        Each numbered paragraph (1., 2., 3., etc.) becomes a section
        Sub-headings (vatthu, kathā) are kept with their following numbered sections
        
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
        pending_title = ''  # Store sub-heading to prepend to next section
        
        for line in lines:
            line_stripped = line.strip()
            
            if not line_stripped:
                # Keep empty lines within sections
                if current_section['pali']:
                    current_section['pali'] += '\n'
                continue
            
            # Check if it's a numbered section (e.g., "1.", "2.", "48.", "10 .")
            # But NOT the main chapter title (e.g., "1. Pāthikasuttaṃ")
            # Note: Some sections have space before period like "10 ."
            numbered_match = re.match(r'^(\d+)\s*\.\s+(.+)', line_stripped)
            
            if numbered_match:
                section_number = numbered_match.group(1)
                content = numbered_match.group(2)
                
                # Check if this is the main chapter title (long title with suttaṃ)
                is_chapter_title = content.endswith('suttaṃ') or content.endswith('suttantaṃ')
                
                if is_chapter_title:
                    # This is the main chapter title, skip or handle separately
                    pending_title = line_stripped
                    continue
                
                # This is a numbered section - start new section
                if current_section['pali'].strip():
                    sections.append(current_section.copy())
                
                section_num = int(section_number)
                current_section = {
                    'number': section_num,
                    'pali': '',
                    'title': pending_title if pending_title else '',
                    'type': 'content'
                }
                
                # Add the content WITHOUT the number (content variable already has it removed)
                # Only add if there's actual content after the number
                if content.strip():
                    current_section['pali'] = content.strip() + '\n'
                pending_title = ''  # Clear pending title
                
            # Check if it's a sub-heading (vatthu, kathā, etc.)
            elif (len(line_stripped) < 100 and 
                  (line_stripped.endswith('vatthu') or 
                   line_stripped.endswith('kathā') or
                   line_stripped.endswith('vaṇṇanā'))):
                # This is a sub-heading - store it to prepend to next section
                pending_title = line_stripped
                
            else:
                # Regular content line - add to current section
                if current_section['pali'] or section_num > 0:
                    current_section['pali'] += line_stripped + '\n'
        
        # Add final section
        if current_section['pali'].strip():
            sections.append(current_section)
        
        logger.info(f"Split text into {len(sections)} sections")
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
    
    def translate_chapter(self, pali_text: str, chapter_id: str, chapter_title: str, resume_from: int = 0, output_path: str = None) -> Dict:
        """
        Translate an entire chapter from Pali to English and Sinhala
        
        Args:
            pali_text: The full Pali text of the chapter
            chapter_id: ID like 'dn1'
            chapter_title: Pali title of the chapter
            resume_from: Section number to resume from (0 = start from beginning)
            output_path: Path to save incremental progress (optional)
        
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
        
        # If resuming, try to load existing partial file
        if resume_from > 0 and output_path and os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    translated_sections = existing_data.get('sections', [])
                    logger.info(f"Loaded {len(translated_sections)} existing sections from {output_path}")
                    print(f"✓ Loaded {len(translated_sections)} existing sections")
            except Exception as e:
                logger.warning(f"Could not load existing file: {e}")
        
        # If resuming, skip already translated sections
        if resume_from > 0:
            print(f"\n🔄 RESUMING from section {resume_from + 1}/{len(sections)}")
            logger.info(f"Resuming translation from section {resume_from + 1}")
        
        for i, section in enumerate(sections, 1):
            # Skip sections if resuming
            if i <= resume_from:
                logger.info(f"Skipping section {i}/{len(sections)} (already translated)")
                continue
            
            logger.info(f"Translating section {i}/{len(sections)}")
            
            # Print progress to console (not just log file)
            print(f"\n[{i}/{len(sections)}] Translating section {section.get('number', i)}...")
            
            pali_text_section = section.get('pali', '').strip()
            title = section.get('title', '').strip()
            
            if not pali_text_section and not title:
                continue
            
            # Translate the content
            if pali_text_section:
                # Phase 1: Primary Translation
                print(f"  → English translation ({len(pali_text_section)} chars)...", end='', flush=True)
                english = self.translate_text(pali_text_section, 'English')
                print(f" ✓ ({len(english)} chars)")
                
                # Validate translation length ratio
                english_ratio = len(english) / len(pali_text_section) if len(pali_text_section) > 0 else 0
                if english_ratio > 5.0:  # Translation is more than 5x the source
                    logger.warning(f"Section {section.get('number', i)}: English translation suspiciously long ({english_ratio:.1f}x source)")
                    logger.warning(f"  Pali: {len(pali_text_section)} chars, English: {len(english)} chars")
                    print(f"  ⚠ Warning: Translation length ratio {english_ratio:.1f}x (may be too long)")
                
                print(f"  → Sinhala translation ({len(pali_text_section)} chars)...", end='', flush=True)
                sinhala = self.translate_text(pali_text_section, 'Sinhala')
                print(f" ✓ ({len(sinhala)} chars)")
                
                # Validate translation length ratio
                sinhala_ratio = len(sinhala) / len(pali_text_section) if len(pali_text_section) > 0 else 0
                if sinhala_ratio > 5.0:  # Translation is more than 5x the source
                    logger.warning(f"Section {section.get('number', i)}: Sinhala translation suspiciously long ({sinhala_ratio:.1f}x source)")
                    logger.warning(f"  Pali: {len(pali_text_section)} chars, Sinhala: {len(sinhala)} chars")
                    print(f"  ⚠ Warning: Translation length ratio {sinhala_ratio:.1f}x (may be too long)")
                
                # Phase 2: Verification & Improvement (if enabled)
                if ENABLE_VERIFICATION:
                    print(f"  → Verifying English...", end='', flush=True)
                    english = self.verify_and_improve_translation(pali_text_section, english, 'English')
                    print(f" ✓ ({len(english)} chars)")
                    
                    print(f"  → Verifying Sinhala...", end='', flush=True)
                    sinhala = self.verify_and_improve_translation(pali_text_section, sinhala, 'Sinhala')
                    print(f" ✓ ({len(sinhala)} chars)")
            else:
                english = ""
                sinhala = ""
            
            # Translate title if exists
            if title:
                english_title = self.translate_text(title, 'English')
                sinhala_title = self.translate_text(title, 'Sinhala')
                
                # If this is a title-only section, put translation in title field
                if not pali_text_section:
                    pali_text_section = title
                    english = english_title
                    sinhala = sinhala_title
                else:
                    # Prepend title to content
                    pali_text_section = title + '\n\n' + pali_text_section
                    english = english_title + '\n\n' + english
                    sinhala = sinhala_title + '\n\n' + sinhala
            
            translated_section = {
                'number': section['number'],
                'pali': pali_text_section,
                'english': english,
                'sinhala': sinhala
            }
            
            translated_sections.append(translated_section)
            
            # Save incremental progress after each section
            if output_path:
                try:
                    # Translate title for chapter metadata
                    english_title = self.translate_text(chapter_title, 'English')
                    sinhala_title = self.translate_text(chapter_title, 'Sinhala')
                    
                    temp_chapter = {
                        'id': chapter_id,
                        'title': {
                            'pali': chapter_title,
                            'english': english_title,
                            'sinhala': sinhala_title
                        },
                        'sections': translated_sections,
                        '_partial': True,  # Mark as partial
                        '_completed_sections': i,
                        '_total_sections': len(sections)
                    }
                    
                    # Save to temporary file first
                    temp_path = output_path + '.partial'
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(temp_chapter, f, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT)
                    
                    # Rename to actual path (atomic operation)
                    os.replace(temp_path, output_path)
                    
                    logger.info(f"Saved progress: {i}/{len(sections)} sections to {output_path}")
                    print(f"  💾 Progress saved ({i}/{len(sections)} sections)")
                except Exception as e:
                    logger.warning(f"Failed to save incremental progress: {e}")
                    # Continue anyway - don't fail the translation
        
        # Create final chapter JSON structure
        # Translate title with validation (if not already done during incremental save)
        english_title = self.translate_text(chapter_title, 'English')
        sinhala_title = self.translate_text(chapter_title, 'Sinhala')
        
        # Validate title length - titles should be short, not full descriptions
        MAX_TITLE_LENGTH = 200  # characters
        if len(english_title) > MAX_TITLE_LENGTH:
            logger.warning(f"English title too long ({len(english_title)} chars), truncating or regenerating")
            # Try to get a shorter title
            short_prompt = f"Translate this Pali title to English. Give ONLY a short title (max 10 words), not a description or summary:\n\n{chapter_title}\n\nEnglish title:"
            try:
                response = self.model.generate_content(short_prompt)
                english_title = self.clean_translation(response.text)
                if len(english_title) > MAX_TITLE_LENGTH:
                    # Still too long, use a generic title
                    logger.warning("Title still too long after retry, using generic title")
                    english_title = f"The {chapter_title} Discourse"
            except Exception as e:
                logger.error(f"Failed to regenerate title: {e}")
                english_title = f"The {chapter_title} Discourse"
        
        if len(sinhala_title) > MAX_TITLE_LENGTH:
            logger.warning(f"Sinhala title too long ({len(sinhala_title)} chars), truncating or regenerating")
            # Try to get a shorter title
            short_prompt = f"Translate this Pali title to Sinhala. Give ONLY a short title (max 10 words), not a description or summary:\n\n{chapter_title}\n\nSinhala title:"
            try:
                response = self.model.generate_content(short_prompt)
                sinhala_title = self.clean_translation(response.text)
                if len(sinhala_title) > MAX_TITLE_LENGTH:
                    # Still too long, use a generic title
                    logger.warning("Title still too long after retry, using generic title")
                    sinhala_title = f"{chapter_title} සූත්‍රය"
            except Exception as e:
                logger.error(f"Failed to regenerate title: {e}")
                sinhala_title = f"{chapter_title} සූත්‍රය"
        
        chapter_json = {
            'id': chapter_id,
            'title': {
                'pali': chapter_title,
                'english': english_title,
                'sinhala': sinhala_title
            },
            'sections': translated_sections
        }
        
        logger.info(f"Chapter {chapter_id} translation completed")
        print(f"\n✅ Chapter {chapter_id} completed! ({len(translated_sections)} sections)")
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
        chapter_marker: Start marker (e.g., "Pāthikasuttaṃ")
        next_chapter_marker: End marker (next chapter title), None for last chapter
    
    Returns:
        Extracted chapter text
    """
    lines = text.split('\n')
    
    start_idx = None
    end_idx = None
    
    # Find the FIRST occurrence with chapter number pattern (e.g., "1. Pāthikasuttaṃ")
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Look for pattern like "1. Pāthikasuttaṃ" at the start of chapter
        if start_idx is None:
            # Match chapter number followed by the marker
            if re.match(r'^\d+\.\s+' + re.escape(chapter_marker), line_stripped):
                start_idx = i
                logger.info(f"Found chapter start at line {i}: {line_stripped[:50]}")
        elif next_chapter_marker:
            # Look for next chapter pattern
            if re.match(r'^\d+\.\s+' + re.escape(next_chapter_marker), line_stripped):
                end_idx = i
                logger.info(f"Found chapter end at line {i}: {line_stripped[:50]}")
                break
    
    if start_idx is None:
        logger.warning(f"Could not find chapter marker: {chapter_marker}")
        return ""
    
    if end_idx is None:
        chapter_lines = lines[start_idx:]
        logger.info(f"Extracting from line {start_idx} to end of file")
    else:
        chapter_lines = lines[start_idx:end_idx]
        logger.info(f"Extracting from line {start_idx} to {end_idx}")
    
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
    pali_file = os.path.join("Pāthikavaggapāḷi", "Pāthikavaggapāḷi_pali_extracted.txt")
    
    try:
        with open(pali_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
        print(f"✓ Loaded Pali text: {len(full_text)} characters")
    except Exception as e:
        print(f"ERROR: Failed to read Pali text file: {e}")
        return
    
    # Read book.json to get chapter information
    book_file = os.path.join("Pāthikavaggapāḷi", "book.json")
    
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
            output_path = os.path.join("Pāthikavaggapāḷi", "chapters", f"{chapter['id']}-{chapter['title']['pali']}.json")
            
            chapter_data = translator.translate_chapter(
                chapter_text,
                chapter['id'],
                chapter['title']['pali'],
                output_path=output_path
            )
            
            # Save final version (without _partial markers)
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

