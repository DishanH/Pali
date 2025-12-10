"""
AI Translator for JSON Chapter Files
Translates Pali text already extracted in JSON format
"""

import google.generativeai as genai
import json
import time
import re
import os
from pathlib import Path
from typing import Dict
import logging
from collections import deque
from datetime import datetime, timedelta

# Import configuration
try:
    from config import (
        MODEL_NAME, VERIFY_MODEL_NAME, ENABLE_VERIFICATION, VERIFY_DELAY,
        RATE_LIMIT_DELAY, TRANSLATION_TEMPERATURE, LOG_LEVEL, LOG_FILE,
        REMOVE_PATTERNS, JSON_INDENT, JSON_ENSURE_ASCII, MAX_RETRIES,
        RETRY_DELAY, SERVER_OVERLOAD_RETRY_DELAY, API_TIMEOUT, MAX_CHUNK_SIZE
    )
except ImportError:
    MODEL_NAME = 'gemini-2.5-flash'
    VERIFY_MODEL_NAME = 'gemini-2.5-flash'
    ENABLE_VERIFICATION = False
    VERIFY_DELAY = 13.0
    RATE_LIMIT_DELAY = 13.0
    TRANSLATION_TEMPERATURE = 0.3
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'translator.log'
    REMOVE_PATTERNS = []
    JSON_INDENT = 2
    JSON_ENSURE_ASCII = False
    MAX_RETRIES = 5
    RETRY_DELAY = 5
    SERVER_OVERLOAD_RETRY_DELAY = 30
    API_TIMEOUT = 120
    MAX_CHUNK_SIZE = 4000

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


class JSONChapterTranslator:
    """Translates Pali text in JSON chapter files to English and Sinhala"""
    
    def __init__(self, api_key: str, rpm_limit: int = 10):
        """Initialize the translator with Google Generative AI
        
        Args:
            api_key: Google API key
            rpm_limit: Requests per minute limit (default: 10 for free tier)
        """
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY", "")
        
        if not api_key:
            raise ValueError("API key is required. Set API_KEY or GOOGLE_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Translator initialized with model: {MODEL_NAME}")
        
        if ENABLE_VERIFICATION:
            self.verify_model = genai.GenerativeModel(VERIFY_MODEL_NAME)
            logger.info(f"Verification model initialized: {VERIFY_MODEL_NAME}")
        else:
            self.verify_model = None
            logger.info("Verification disabled")
        
        # Rate limiting - track API call timestamps
        self.rpm_limit = rpm_limit
        self.api_call_times = deque(maxlen=rpm_limit)
        logger.info(f"Rate limiter initialized: {rpm_limit} RPM")
    
    def enforce_rate_limit(self):
        """Enforce RPM limit by waiting if necessary"""
        now = datetime.now()
        
        # If we haven't made rpm_limit calls yet, no need to wait
        if len(self.api_call_times) < self.rpm_limit:
            self.api_call_times.append(now)
            return
        
        # Check oldest call time
        oldest_call = self.api_call_times[0]
        time_since_oldest = (now - oldest_call).total_seconds()
        
        # If oldest call was less than 60 seconds ago, we need to wait
        if time_since_oldest < 60:
            wait_time = 60 - time_since_oldest + 1  # Add 1 second buffer
            logger.info(f"Rate limit: {self.rpm_limit} RPM reached. Waiting {wait_time:.1f}s...")
            print(f"  ⏱️  Rate limit protection: waiting {wait_time:.1f}s (made {self.rpm_limit} calls in last {time_since_oldest:.0f}s)")
            time.sleep(wait_time)
        
        # Record this API call
        self.api_call_times.append(datetime.now())
    
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
        
        # Remove leading section numbers
        text = re.sub(r'^\s*\d+\s*\.\s+', '', text, flags=re.MULTILINE)
        
        # CRITICAL: Replace literal <ZWJ> text with actual Zero-Width Joiner (U+200D)
        # Sometimes AI outputs <ZWJ> as visible text instead of the actual invisible character
        text = text.replace('<ZWJ>', '\u200D')
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = text.strip()
        
        return text
    
    def split_text_into_chunks(self, text: str, max_size: int = None) -> list:
        """Split large text into smaller chunks at sentence boundaries
        
        Uses a three-tier approach for clean splits:
        1. Try paragraph breaks first (\n\n)
        2. Then sentence endings (., !, ?, etc.)
        3. Force mid-sentence split only as last resort
        
        This ensures translation quality by preserving context.
        """
        if max_size is None:
            max_size = MAX_CHUNK_SIZE
        
        if len(text) <= max_size:
            return [text]
        
        # Try to split at paragraph breaks first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # If single paragraph is too large, split at sentences
            if len(para) > max_size:
                # Split at sentence boundaries with improved Pali/Buddhist text support
                # Handles: period, exclamation, question mark, Devanagari danda (।), double danda (॥)
                # Now also handles punctuation at end of text (with or without trailing space)
                # Pattern explanation:
                #   [.!?।॥]+ - one or more sentence-ending punctuation marks
                #   (?:\s+|$) - followed by whitespace OR end of string (non-capturing)
                sentences = re.split(r'([.!?।॥]+(?:\s+|$))', para)
                
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i] if i < len(sentences) else ""
                    delimiter = sentences[i+1] if i+1 < len(sentences) else ""
                    full_sentence = sentence + delimiter
                    
                    # Skip empty sentences
                    if not full_sentence.strip():
                        continue
                    
                    if len(current_chunk) + len(full_sentence) > max_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = full_sentence
                        else:
                            # Sentence itself is too large, force split
                            # This should be rare - only for very long sentences
                            logger.warning(f"Sentence exceeds max_size ({len(full_sentence)} > {max_size}), forcing mid-sentence split")
                            chunks.append(full_sentence[:max_size].strip())
                            current_chunk = full_sentence[max_size:]
                    else:
                        current_chunk += full_sentence
            else:
                # Normal paragraph handling
                if len(current_chunk) + len(para) + 2 > max_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Split {len(text)} chars into {len(chunks)} chunks at natural boundaries")
        return chunks
    
    def translate_text(self, pali_text: str, target_language: str, retry_count: int = 0, max_retries: int = None) -> str:
        """Translate Pali text to target language"""
        if not pali_text.strip():
            return ""
        
        if max_retries is None:
            max_retries = MAX_RETRIES
        
        # Check if text is too large and needs to be split
        if len(pali_text) > MAX_CHUNK_SIZE:
            logger.warning(f"Text too large ({len(pali_text)} chars), splitting into chunks")
            print(f"  ⚠️  Text is large ({len(pali_text)} chars), splitting into chunks...")
            
            chunks = self.split_text_into_chunks(pali_text)
            logger.info(f"Split into {len(chunks)} chunks")
            print(f"  📦 Split into {len(chunks)} chunks")
            
            translated_chunks = []
            for i, chunk in enumerate(chunks, 1):
                print(f"    → Chunk {i}/{len(chunks)} ({len(chunk)} chars)...", end='', flush=True)
                try:
                    translated = self.translate_text(chunk, target_language, 0, max_retries)
                    translated_chunks.append(translated)
                    print(f" ✓")
                except Exception as e:
                    logger.error(f"Failed to translate chunk {i}: {e}")
                    print(f" ❌")
                    raise
            
            # Combine chunks with proper spacing
            result = "\n\n".join(translated_chunks)
            logger.info(f"Combined {len(chunks)} chunks into {len(result)} chars")
            return result
        
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
- IMPORTANT: Translate Pali terms with their full philosophical meaning, not literal word-by-word
  Example: "Khaṇakicco" means "has a duty/task that must be done in this moment" NOT just "momentary"
  Preserve the nuanced doctrinal meaning rather than simplified modern interpretations

Translation Requirements:
1. Preserve the exact doctrinal and philosophical meaning
2. Keep traditional Buddhist terminology accurate
3. Use modern, accessible language that's easy to understand
4. Preserve paragraph breaks and structure
5. Handle Pali Unicode characters correctly
6. IMPORTANT: Complete ALL sentences - do not truncate
7. Ensure the translation flows naturally and is grammatically complete

Pali Text:
{pali_text}

{target_language} Translation:"""
        
        try:
            logger.info(f"Translating {len(pali_text)} characters to {target_language}")
            
            # Enforce rate limit BEFORE making API call
            self.enforce_rate_limit()
            
            # Set timeout for API request
            response = self.model.generate_content(
                prompt,
                request_options={"timeout": API_TIMEOUT}
            )
            
            # Check finish_reason BEFORE accessing response.text
            if hasattr(response, 'candidates') and response.candidates:
                finish_reason = response.candidates[0].finish_reason
                
                # finish_reason values: 1=STOP (normal), 2=MAX_TOKENS, 3=SAFETY, 4=RECITATION, 5=OTHER, 8=BLOCKED
                if finish_reason in [3, 4, 5, 8]:
                    logger.warning(f"Response blocked with finish_reason: {finish_reason}")
                    
                    if retry_count < max_retries:
                        wait_time = (2 ** retry_count) * RETRY_DELAY
                        logger.info(f"Retrying after {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                        print(f"  ⚠ Response blocked (reason {finish_reason}), retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        return self.translate_text(pali_text, target_language, retry_count + 1, max_retries)
                    else:
                        raise ValueError(f"Translation blocked by API (finish_reason: {finish_reason}) after {max_retries} retries")
            
            # Now safe to access response.text
            if not response.text or not response.text.strip():
                raise ValueError("Empty response from API")
            
            translation = response.text
            translation = self.clean_translation(translation)
            
            logger.info(f"Translation completed: {len(translation)} characters")
            time.sleep(RATE_LIMIT_DELAY)
            
            return translation
            
        except ValueError as e:
            logger.error(f"Translation error: {str(e)}")
            raise
        except Exception as e:
            error_str = str(e).lower()
            error_code = str(e)
            logger.error(f"Translation error: {str(e)}")
            
            # Check for 504 Gateway Timeout / Stream Cancelled (text too large or model overload)
            if '504' in error_code or 'stream cancelled' in error_str or 'gateway timeout' in error_str or 'deadline exceeded' in error_str:
                # If text is large, try splitting it
                if len(pali_text) > MAX_CHUNK_SIZE / 2 and retry_count == 0:
                    logger.warning(f"504 timeout with {len(pali_text)} chars, trying smaller chunks")
                    print(f"  ⚠️  Request timeout (504) - text may be too large ({len(pali_text)} chars)")
                    print(f"  📦 Splitting into smaller chunks and retrying...")
                    
                    # Force smaller chunks for retry
                    smaller_chunk_size = MAX_CHUNK_SIZE // 2
                    chunks = self.split_text_into_chunks(pali_text, smaller_chunk_size)
                    
                    translated_chunks = []
                    for i, chunk in enumerate(chunks, 1):
                        print(f"    → Chunk {i}/{len(chunks)} ({len(chunk)} chars)...", end='', flush=True)
                        try:
                            translated = self.translate_text(chunk, target_language, 0, max_retries)
                            translated_chunks.append(translated)
                            print(f" ✓")
                        except Exception as chunk_error:
                            logger.error(f"Failed to translate chunk {i}: {chunk_error}")
                            print(f" ❌")
                            raise
                    
                    result = "\n\n".join(translated_chunks)
                    logger.info(f"Successfully translated using {len(chunks)} smaller chunks")
                    return result
                
                # Regular retry with backoff
                if retry_count < max_retries:
                    wait_time = SERVER_OVERLOAD_RETRY_DELAY * (retry_count + 1)
                    logger.warning(f"504 Gateway Timeout, waiting {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                    print(f"  ⚠️  Gateway timeout (504)! Waiting {wait_time}s before retry... (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(wait_time)
                    return self.translate_text(pali_text, target_language, retry_count + 1, max_retries)
                else:
                    raise Exception(f"Request timed out after {max_retries} retries. Try reducing MAX_CHUNK_SIZE in config.py or the section may be too complex.")
            
            # Check for 503 Server Overload errors (model is busy, not a rate limit)
            if '503' in error_code or 'overloaded' in error_str or 'server error' in error_str:
                if retry_count < max_retries:
                    # Use longer delay for server overload
                    wait_time = SERVER_OVERLOAD_RETRY_DELAY * (retry_count + 1)  # Linear increase: 30s, 60s, 90s...
                    logger.warning(f"Server overload (503), waiting {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                    print(f"  ⚠ Server overloaded! Waiting {wait_time}s before retry... (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(wait_time)
                    return self.translate_text(pali_text, target_language, retry_count + 1, max_retries)
                else:
                    raise Exception(f"Server overloaded after {max_retries} retries. The model is experiencing high demand. Please try again in a few minutes.")
            
            # Check for rate limit errors
            if '429' in error_code or 'rate limit' in error_str or 'quota' in error_str or 'resource exhausted' in error_str:
                if retry_count < max_retries:
                    wait_time = (2 ** retry_count) * RETRY_DELAY * 2  # Exponential backoff
                    logger.warning(f"Rate limit hit, waiting {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                    print(f"  ⚠ Rate limit exceeded! Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    return self.translate_text(pali_text, target_language, retry_count + 1, max_retries)
                else:
                    raise Exception(f"Rate limit exceeded after {max_retries} retries. Please wait and try again later.")
            
            # Check for timeout errors
            if 'timeout' in error_str or 'deadline exceeded' in error_str:
                if retry_count < max_retries:
                    wait_time = RETRY_DELAY * (retry_count + 1)
                    logger.warning(f"Timeout error, retrying after {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                    print(f"  ⚠ Request timeout! Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    return self.translate_text(pali_text, target_language, retry_count + 1, max_retries)
                else:
                    raise Exception(f"Request timed out after {max_retries} retries.")
            
            # Check for finish_reason errors
            if "finish_reason" in error_str:
                if retry_count < max_retries:
                    wait_time = (2 ** retry_count) * RETRY_DELAY
                    logger.info(f"Retrying after {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                    print(f"  ⚠ API error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    return self.translate_text(pali_text, target_language, retry_count + 1, max_retries)
                else:
                    logger.error(f"Translation failed after {max_retries} retries")
            
            raise
    
    def verify_and_improve_translation(self, pali_text: str, translated_text: str, target_language: str, retry_count: int = 0, max_retries: int = None) -> str:
        """Verify translation accuracy and improve readability"""
        if not ENABLE_VERIFICATION or not self.verify_model:
            return translated_text
        
        if max_retries is None:
            max_retries = MAX_RETRIES
        
        if not pali_text.strip() or not translated_text.strip():
            return translated_text
        
        prompt = f"""You are verifying a {target_language} translation of Pali Buddhist text.

ORIGINAL PALI TEXT:
{pali_text}

CURRENT {target_language.upper()} TRANSLATION:
{translated_text}

YOUR TASK:
1. Verify the translation is accurate and complete
2. Improve readability while preserving exact meaning
3. Fix any errors or awkward phrasing
4. For Sinhala: Use ONLY proper Sinhala Unicode characters (U+0D80-U+0DFF range). DO NOT use Tamil, Hindi, Telugu, Kannada, Bengali or other Indian script characters.
5. Return ONLY the improved {target_language} translation

IMPROVED {target_language.upper()} TRANSLATION:"""
        
        try:
            logger.info(f"Verifying {target_language} translation ({len(translated_text)} chars)")
            
            # Enforce rate limit BEFORE making API call
            self.enforce_rate_limit()
            
            response = self.verify_model.generate_content(
                prompt,
                request_options={"timeout": API_TIMEOUT}
            )
            verified_text = response.text
            verified_text = self.clean_translation(verified_text)
            
            # Validate and fix Sinhala characters
            if target_language == 'Sinhala':
                is_valid, issues = self.validate_sinhala_characters(verified_text)
                if not is_valid:
                    logger.warning(f"Foreign characters detected in Sinhala: {len(issues)} issues")
                    for issue in issues[:3]:
                        logger.warning(f"  {issue['script']} char '{issue['char']}' ({issue['unicode']}) at position {issue['position']}")
                    
                    # Try to fix foreign characters
                    fix_prompt = f"""The following Sinhala text contains FOREIGN script characters from other Indian languages.
Please rewrite it using ONLY proper Sinhala Unicode characters (U+0D80-U+0DFF).

Replace all foreign characters with proper Sinhala equivalents:

PROBLEMATIC TEXT:
{verified_text}

ISSUES FOUND:
{chr(10).join([f"- {issue['script']} character '{issue['char']}' ({issue['unicode']}) in: ...{issue['context']}..." for issue in issues[:5]])}

CORRECTED SINHALA TEXT (using ONLY Sinhala Unicode U+0D80-U+0DFF):"""
                    
                    try:
                        logger.info("Attempting to fix foreign characters in Sinhala text")
                        
                        # Enforce rate limit BEFORE making API call
                        self.enforce_rate_limit()
                        
                        fix_response = self.verify_model.generate_content(fix_prompt)
                        fixed_text = self.clean_translation(fix_response.text)
                        
                        # Validate again
                        is_valid_now, remaining_issues = self.validate_sinhala_characters(fixed_text)
                        if is_valid_now:
                            logger.info("Successfully corrected all foreign characters")
                            verified_text = fixed_text
                        else:
                            logger.warning(f"Still {len(remaining_issues)} foreign characters remain after fix attempt")
                            # Use fixed text anyway as it's likely better
                            verified_text = fixed_text
                        
                        time.sleep(VERIFY_DELAY)  # Additional delay for fix attempt
                    except Exception as fix_error:
                        logger.warning(f"Failed to fix foreign characters: {str(fix_error)}")
            
            logger.info(f"Verification completed")
            time.sleep(VERIFY_DELAY)
            
            return verified_text
            
        except Exception as e:
            error_str = str(e).lower()
            error_code = str(e)
            
            # Check for 503 Server Overload
            if '503' in error_code or 'overloaded' in error_str:
                if retry_count < max_retries:
                    wait_time = SERVER_OVERLOAD_RETRY_DELAY * (retry_count + 1)
                    logger.warning(f"Server overload in verification, waiting {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                    print(f"  ⚠ Server overloaded during verification! Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    return self.verify_and_improve_translation(pali_text, translated_text, target_language, retry_count + 1, max_retries)
            
            # Check for rate limit errors
            if '429' in error_code or 'rate limit' in error_str or 'quota' in error_str:
                if retry_count < max_retries:
                    wait_time = (2 ** retry_count) * RETRY_DELAY * 2  # Exponential backoff
                    logger.warning(f"Rate limit in verification, retrying after {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                    print(f"  ⚠ Rate limit hit during verification, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    return self.verify_and_improve_translation(pali_text, translated_text, target_language, retry_count + 1, max_retries)
            
            # Check for timeout errors
            if 'timeout' in error_str or 'deadline exceeded' in error_str:
                if retry_count < max_retries:
                    wait_time = RETRY_DELAY * (retry_count + 1)
                    logger.warning(f"Timeout in verification, retrying after {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                    print(f"  ⚠ Timeout during verification! Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    return self.verify_and_improve_translation(pali_text, translated_text, target_language, retry_count + 1, max_retries)
            
            logger.warning(f"Verification failed: {str(e)}. Using original translation.")
            return translated_text
    
    def translate_json_chapter(self, json_path: str, resume_from: int = 0, auto_resume: bool = True) -> Dict:
        """
        Translate a JSON chapter file
        
        Args:
            json_path: Path to the JSON file
            resume_from: Section index to resume from (0 = start from beginning)
            auto_resume: Automatically resume on exceptions after a delay
        
        Returns:
            Updated chapter data
        """
        logger.info(f"Processing JSON file: {json_path}")
        print(f"\n{'='*60}")
        print(f"Processing: {json_path}")
        print(f"{'='*60}\n")
        
        # Load JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data.get('id', 'unknown')
        sections = chapter_data.get('sections', [])
        
        logger.info(f"Loaded chapter {chapter_id} with {len(sections)} sections")
        print(f"Chapter ID: {chapter_id}")
        print(f"Total sections: {len(sections)}")
        
        # Translate chapter title if missing
        title_obj = chapter_data.get('title', {})
        pali_title = title_obj.get('pali', '')
        
        if pali_title and (not title_obj.get('english') or not title_obj.get('sinhala')):
            print(f"\n📖 Translating chapter title: {pali_title}")
            
            if not title_obj.get('english'):
                print(f"  → English title...", end='', flush=True)
                english_title = self.translate_text(pali_title, 'English')
                
                # Validate title length
                MAX_TITLE_LENGTH = 200
                if len(english_title) > MAX_TITLE_LENGTH:
                    logger.warning(f"English title too long ({len(english_title)} chars)")
                    short_prompt = f"Translate this Pali title to English. Give ONLY a short title (max 10 words):\n\n{pali_title}\n\nEnglish title:"
                    try:
                        self.enforce_rate_limit()
                        response = self.model.generate_content(short_prompt)
                        english_title = self.clean_translation(response.text)
                    except:
                        english_title = f"The {pali_title} Discourse"
                
                title_obj['english'] = english_title
                print(f" ✓ ({len(english_title)} chars)")
            
            if not title_obj.get('sinhala'):
                print(f"  → Sinhala title...", end='', flush=True)
                sinhala_title = self.translate_text(pali_title, 'Sinhala')
                
                MAX_TITLE_LENGTH = 200
                if len(sinhala_title) > MAX_TITLE_LENGTH:
                    logger.warning(f"Sinhala title too long ({len(sinhala_title)} chars)")
                    short_prompt = f"Translate this Pali title to Sinhala. Give ONLY a short title (max 10 words):\n\n{pali_title}\n\nSinhala title:"
                    try:
                        self.enforce_rate_limit()
                        response = self.model.generate_content(short_prompt)
                        sinhala_title = self.clean_translation(response.text)
                    except:
                        sinhala_title = f"{pali_title} සූත්‍රය"
                
                title_obj['sinhala'] = sinhala_title
                print(f" ✓ ({len(sinhala_title)} chars)")
            
            chapter_data['title'] = title_obj
        
        # Resume logic
        if resume_from > 0:
            print(f"\n🔄 RESUMING from section {resume_from + 1}/{len(sections)}")
            logger.info(f"Resuming translation from section {resume_from + 1}")
        
        # Translate sections
        for i, section in enumerate(sections):
            if i < resume_from:
                logger.info(f"Skipping section {i+1}/{len(sections)} (already translated)")
                continue
            
            section_num = section.get('number', i+1)
            pali_text = section.get('pali', '').strip()
            pali_title = section.get('paliTitle', '').strip()
            
            if not pali_text and not pali_title:
                logger.info(f"Skipping empty section {i+1}")
                continue
            
            print(f"\n[{i+1}/{len(sections)}] Section {section_num}")
            
            # Translate paliTitle if exists and not already translated
            if pali_title:
                print(f"  📌 Title: {pali_title[:50]}...")
            
            # Translate main content with exception handling
            try:
                if pali_text:
                    # Check if already translated
                    has_english = section.get('english', '').strip()
                    has_sinhala = section.get('sinhala', '').strip()
                    
                    if not has_english:
                        print(f"  → English ({len(pali_text)} chars)...", end='', flush=True)
                        english = self.translate_text(pali_text, 'English')
                        print(f" ✓ ({len(english)} chars)")
                        
                        # Validate length ratio
                        ratio = len(english) / len(pali_text) if len(pali_text) > 0 else 0
                        if ratio > 5.0:
                            logger.warning(f"Section {section_num}: English translation suspiciously long ({ratio:.1f}x)")
                            print(f"  ⚠ Warning: Translation length ratio {ratio:.1f}x")
                        
                        if ENABLE_VERIFICATION:
                            print(f"  → Verifying English...", end='', flush=True)
                            english = self.verify_and_improve_translation(pali_text, english, 'English')
                            print(f" ✓")
                        
                        section['english'] = english
                    else:
                        print(f"  ✓ English already translated")
                    
                    if not has_sinhala:
                        print(f"  → Sinhala ({len(pali_text)} chars)...", end='', flush=True)
                        sinhala = self.translate_text(pali_text, 'Sinhala')
                        print(f" ✓ ({len(sinhala)} chars)")
                        
                        ratio = len(sinhala) / len(pali_text) if len(pali_text) > 0 else 0
                        if ratio > 5.0:
                            logger.warning(f"Section {section_num}: Sinhala translation suspiciously long ({ratio:.1f}x)")
                            print(f"  ⚠ Warning: Translation length ratio {ratio:.1f}x")
                        
                        if ENABLE_VERIFICATION:
                            print(f"  → Verifying Sinhala...", end='', flush=True)
                            sinhala = self.verify_and_improve_translation(pali_text, sinhala, 'Sinhala')
                            print(f" ✓")
                        
                        section['sinhala'] = sinhala
                    else:
                        print(f"  ✓ Sinhala already translated")
                
                # Save progress after each section
                try:
                    temp_path = json_path + '.partial'
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(chapter_data, f, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT)
                    os.replace(temp_path, json_path)
                    print(f"  💾 Progress saved ({i+1}/{len(sections)} sections)")
                    logger.info(f"Saved progress: {i+1}/{len(sections)} sections")
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
                    print(f"\n💡 To resume later, use: resume_from={i+1}")
                    raise Exception(f"Quota exceeded at section {i+1}. Resume with: resume_from={i+1}")
                
                # For other errors, try to resume if auto_resume is enabled
                if auto_resume and i < len(sections) - 1:
                    wait_time = 10
                    print(f"\n⏳ Waiting {wait_time} seconds before resuming from section {i+1}...")
                    logger.info(f"Auto-resuming after {wait_time}s delay")
                    time.sleep(wait_time)
                    
                    # Recursively call with resume_from set to current section
                    print(f"\n🔄 Auto-resuming from section {i+1}...")
                    return self.translate_json_chapter(json_path, resume_from=i, auto_resume=auto_resume)
                else:
                    # Re-raise the exception if auto_resume is disabled or it's the last section
                    raise
        
        logger.info(f"Chapter {chapter_id} translation completed")
        print(f"\n✅ Chapter {chapter_id} completed! ({len(sections)} sections)")
        
        return chapter_data
    
    def save_chapter_json(self, chapter_data: Dict, output_path: str):
        """Save chapter data to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chapter_data, f, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT)
        
        logger.info(f"Saved chapter to {output_path}")


def check_file_needs_translation(json_path: str) -> tuple:
    """
    Check if a JSON file needs translation
    
    Returns:
        (needs_translation: bool, missing_count: int, total_sections: int)
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        sections = chapter_data.get('sections', [])
        missing_count = 0
        
        # Check title
        title_obj = chapter_data.get('title', {})
        pali_title = title_obj.get('pali', '')
        if pali_title and (not title_obj.get('english') or not title_obj.get('sinhala')):
            missing_count += 1
        
        # Check sections
        for section in sections:
            pali_text = section.get('pali', '').strip()
            if pali_text:
                if not section.get('english', '').strip() or not section.get('sinhala', '').strip():
                    missing_count += 1
        
        return missing_count > 0, missing_count, len(sections)
    except Exception as e:
        logger.warning(f"Error checking file {json_path}: {e}")
        return False, 0, 0


def get_json_files_from_path(input_path: str) -> list:
    """
    Get list of JSON files from input path (file or directory)
    
    Args:
        input_path: Path to a JSON file or a directory containing JSON files
    
    Returns:
        List of JSON file paths
    """
    input_path = input_path.strip().strip('"\'')
    
    if os.path.isfile(input_path):
        if input_path.endswith('.json'):
            return [input_path]
        else:
            logger.warning(f"File {input_path} is not a JSON file")
            return []
    
    elif os.path.isdir(input_path):
        json_files = []
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.endswith('.json') and not file.endswith('.partial'):
                    json_files.append(os.path.join(root, file))
        return sorted(json_files)
    
    else:
        logger.warning(f"Path {input_path} does not exist")
        return []


def main():
    """Main execution function"""
    print("=" * 60)
    print("JSON Chapter Translator for Pali Buddhist Texts")
    print("=" * 60)
    
    # Get API key
    api_key = input("Enter your Google Generative AI API key (or press Enter to use env variable): ").strip()
    
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY", "")
    
    if not api_key:
        print("ERROR: No API key provided. Set GOOGLE_API_KEY environment variable or enter it when prompted.")
        return
    
    # Get RPM limit
    rpm_input = input("\nEnter your API RPM limit (5 for gemini-2.5-flash, 10 for older models, press Enter for default 5): ").strip()
    rpm_limit = 5  # Default for gemini-2.5-flash (Dec 2024)
    if rpm_input:
        try:
            rpm_limit = int(rpm_input)
            if rpm_limit < 1:
                print("Invalid RPM limit, using default: 5")
                rpm_limit = 5
        except ValueError:
            print("Invalid input, using default RPM limit: 5")
    
    print(f"✓ Using RPM limit: {rpm_limit} requests per minute")
    
    # Initialize translator
    try:
        translator = JSONChapterTranslator(api_key, rpm_limit=rpm_limit)
    except Exception as e:
        print(f"ERROR: Failed to initialize translator: {e}")
        return
    
    # Get input path (file or folder)
    input_path = input("\nEnter path to JSON file or chapters folder: ").strip()
    
    if not os.path.exists(input_path):
        print(f"ERROR: Path not found: {input_path}")
        return
    
    # Get list of JSON files
    json_files = get_json_files_from_path(input_path)
    
    if not json_files:
        print(f"ERROR: No JSON files found in: {input_path}")
        return
    
    print(f"\n📁 Found {len(json_files)} JSON file(s)")
    
    # Check which files need translation
    files_to_process = []
    for json_file in json_files:
        needs_translation, missing_count, total_sections = check_file_needs_translation(json_file)
        if needs_translation:
            files_to_process.append((json_file, missing_count, total_sections))
            print(f"  ⚠️  {os.path.basename(json_file)} - {missing_count} missing translation(s)")
        else:
            print(f"  ✓  {os.path.basename(json_file)} - fully translated")
    
    if not files_to_process:
        print("\n✅ All files are fully translated! Nothing to do.")
        return
    
    print(f"\n📝 {len(files_to_process)} file(s) need translation")
    
    # Ask for confirmation
    confirm = input(f"\nProcess {len(files_to_process)} file(s)? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("Cancelled by user")
        return
    
    # Ask about auto-resume
    auto_resume_input = input("\nAuto-resume on errors? (Y/n): ").strip().lower()
    auto_resume = auto_resume_input != 'n'
    
    if auto_resume:
        print("✓ Auto-resume enabled - will retry after 10 seconds on errors")
    else:
        print("✓ Auto-resume disabled - will stop on first error")
    
    # Process files
    processed_count = 0
    failed_files = []
    
    for idx, (json_file, missing_count, total_sections) in enumerate(files_to_process, 1):
        print(f"\n{'='*60}")
        print(f"File {idx}/{len(files_to_process)}: {os.path.basename(json_file)}")
        print(f"{'='*60}")
        
        try:
            chapter_data = translator.translate_json_chapter(json_file, resume_from=0, auto_resume=auto_resume)
            translator.save_chapter_json(chapter_data, json_file)
            print(f"\n✓ Completed: {json_file}")
            processed_count += 1
        except Exception as e:
            error_str = str(e).lower()
            print(f"\n❌ FAILED: {json_file}")
            print(f"   Error: {e}")
            logger.exception(f"Failed to process {json_file}:")
            failed_files.append((json_file, str(e)))
            
            # Check if it's a quota error - stop processing
            if 'quota' in error_str or 'rate limit' in error_str or '429' in str(e):
                print(f"\n⛔ QUOTA EXCEEDED - Stopping batch processing")
                print(f"   Processed {processed_count}/{len(files_to_process)} files")
                print(f"   Remaining: {len(files_to_process) - processed_count} files")
                break
            
            # For other errors, ask if should continue
            if idx < len(files_to_process):
                continue_input = input(f"\nContinue to next file? (Y/n): ").strip().lower()
                if continue_input == 'n':
                    print("Stopped by user")
                    break
    
    # Summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"✓ Successfully processed: {processed_count}/{len(files_to_process)} files")
    
    if failed_files:
        print(f"\n❌ Failed files ({len(failed_files)}):")
        for file_path, error in failed_files:
            print(f"  • {os.path.basename(file_path)}")
            print(f"    Error: {error[:100]}...")
    
    print("\n" + "=" * 60)
    print("Translation process completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
