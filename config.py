"""
Configuration file for Pali Translator
Adjust these settings based on your needs and API limits

QUICK SETUP:
- Free Tier (15 RPM): Set RATE_LIMIT_DELAY = 5, VERIFY_DELAY = 5
- Paid Tier (1K RPM): Set RATE_LIMIT_DELAY = 0.5, VERIFY_DELAY = 0.5  [CURRENT]

See PAID_TIER_OPTIMIZATION.md for detailed guide.
"""

# ============================================================================
# API Configuration
# ============================================================================

# Google Generative AI Model for Primary Translation
# Options: 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash-exp', 'gemini-pro'
# Note: Different models have different rate limits and capabilities
# gemini-2.5-flash has been VERY SLOW - switching to gemini-1.5-flash for reliability
MODEL_NAME = 'gemini-2.5-flash'

# Google Generative AI Model for Verification & Readability Enhancement
# This model checks the primary translation and improves readability
# Can be same or different from MODEL_NAME
# Recommended: Use a more powerful model for verification (e.g., gemini-1.5-pro)
VERIFY_MODEL_NAME = 'gemini-2.5-flash'

# Enable two-phase translation with verification
# If False, only primary translation is used
# WARNING: Verification DOUBLES token usage (sends Pali + Translation together)
# For paid tier with large sections: May hit TPM (Token Per Minute) limits
# Recommendation: Use longer delays to avoid 429 errors
ENABLE_VERIFICATION = False  # Disabled to reduce API calls and avoid rate limits

# Verification delay (seconds) - separate from primary translation delay
# Recommend higher value to avoid rate limits
# This is in ADDITION to the RATE_LIMIT_DELAY before each verification
VERIFY_DELAY = 3.0  # Longer delay for verification (sends large prompts)

# ============================================================================
# Rate Limiting Configuration
# ============================================================================

# Delay between API calls (seconds)
# Increase this if you hit rate limits
# For 10 RPM limit: Need 6+ seconds between calls (60s / 10 requests = 6s)
# For 15 RPM limit: Need 4+ seconds between calls (60s / 15 requests = 4s)
# Recommended: 7 seconds for 10 RPM tier to have safety margin
# Note: Each section typically makes 2 API calls (English + Sinhala)
# IMPORTANT: If you still hit limits, increase this to 8-10 seconds
RATE_LIMIT_DELAY = 7.0  # Safe for 10 RPM limit (60/10 = 6s minimum)

# Maximum retries for failed API calls
MAX_RETRIES = 5  # Increased for 503 overload errors

# Delay between retries (seconds) - base delay for exponential backoff
RETRY_DELAY = 5

# Special delay for 503 Server Overload errors (longer wait needed)
SERVER_OVERLOAD_RETRY_DELAY = 30

# API request timeout (seconds)
# Maximum time to wait for a single API response
# If exceeded, will retry with exponential backoff
API_TIMEOUT = 120  # 2 minutes max per request

# ============================================================================
# Text Processing Configuration
# ============================================================================

# Maximum characters per translation chunk
# Keep under 5000 for best results
# Gemini Flash supports up to ~30K tokens, but smaller chunks = better translations
MAX_CHUNK_SIZE = 4000

# Minimum characters for a section to be processed independently
# Sections smaller than this will be combined with neighbors
MIN_SECTION_SIZE = 100

# Maximum characters for a section before it's split
# Should be same as MAX_CHUNK_SIZE or larger
MAX_SECTION_SIZE = 4000

# ============================================================================
# Translation Quality Configuration
# ============================================================================

# Temperature for translation (0.0 - 1.0)
# Lower = more conservative/literal, Higher = more creative
# Recommended: 0.3-0.5 for religious texts
TRANSLATION_TEMPERATURE = 0.3

# Whether to include Pali terms in parentheses for technical terms
INCLUDE_PALI_TERMS = True

# ============================================================================
# File Path Configuration
# ============================================================================

# Input directory containing Pali texts
INPUT_DIR = "Pāthikavaggapāḷi"

# Output directory for translated JSON files
OUTPUT_DIR = "Pāthikavaggapāḷi/chapters"

# Pali source file name
PALI_SOURCE_FILE = "Pāthikavaggapāḷi_pali_extracted.txt"

# Book metadata file
BOOK_METADATA_FILE = "book.json"

# ============================================================================
# Logging Configuration
# ============================================================================

# Logging level
# Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
LOG_LEVEL = 'INFO'

# Log file path (None = console only)
LOG_FILE = 'translator.log'

# ============================================================================
# Translation Prompt Templates
# ============================================================================

ENGLISH_TRANSLATION_INSTRUCTIONS = """
Translation Requirements for English:
1. Use clear, modern English that's accessible to contemporary readers
2. Preserve exact Buddhist doctrinal and philosophical meanings
3. Keep traditional Buddhist terminology (dhamma, karma, nibbana, bhikkhu, sangha)
4. Explain complex concepts in everyday language while maintaining accuracy
5. Use active voice where possible for better readability
6. Maintain paragraph structure and breaks
7. Complete all sentences - no truncation
8. Provide Pali terms in parentheses for key Buddhist concepts (first occurrence only)
9. Use formal but accessible language appropriate for religious texts
10. Ensure grammatical correctness and natural flow
"""

SINHALA_TRANSLATION_INSTRUCTIONS = """
Translation Requirements for Sinhala:
1. Use proper Sinhala script (not romanized)
2. Preserve exact Buddhist doctrinal and philosophical meanings
3. Use traditional Sinhala Buddhist terminology accurately
4. Maintain respectful language appropriate for Dhamma texts
5. Keep paragraph structure and breaks
6. Complete all sentences properly
7. Use classical Sinhala for formal terms, colloquial for explanations
8. CRITICAL: Translate Pali terms with their full philosophical meaning, not literal word-by-word
   - Example: "Khaṇakicco" = "මේ මොහොතේම සිදු කළ යුතු කර්තව්‍යය ඇති" (has a duty that must be done in this moment)
   - NOT: "ක්ෂණකාරී" (momentary) which is ambiguous and loses the doctrinal meaning
   - Preserve nuanced Buddhist doctrinal meanings rather than simplified modern interpretations
9. Ensure proper grammar and natural Sinhala sentence flow
10. Include Pali terms in Sinhala script where traditional
11. Make text accessible to modern Sinhala readers while maintaining dignity
"""

# ============================================================================
# Verification Prompt Templates
# ============================================================================

VERIFICATION_INSTRUCTIONS = """
You are a Buddhist scholar and translation quality expert. Your task is to verify and improve a translation.

VERIFICATION CHECKLIST:
1. **Accuracy**: Does the translation preserve ALL content from the Pali?
   - Check for omissions or additions
   - Verify doctrinal terms are correct
   - Ensure no meaning is lost or distorted

2. **Completeness**: Is there 1-to-1 mapping?
   - Every Pali concept has a corresponding translation
   - No extra explanations or commentary added
   - All sentences are complete

3. **Readability**: Is the language natural and modern?
   - Improve sentence flow if awkward
   - Use contemporary {language} while preserving meaning
   - Make complex ideas accessible without oversimplifying

4. **Terminology**: Are Buddhist terms used correctly?
   - Traditional terms (dhamma, karma, nibbana) preserved
   - Technical terms translated consistently
   - Pali terms in parentheses where appropriate

YOUR TASK:
- If translation is accurate but awkward → Improve readability while keeping exact meaning
- If translation has errors → Fix them and note what was wrong
- If translation is excellent → Return it as-is with confirmation

OUTPUT FORMAT:
Return ONLY the improved {language} translation. Do not add:
- Explanatory notes
- Commentary
- Meta-information
- Headers or footers

Just the clean, improved translation text.
"""

# ============================================================================
# Content Cleaning Configuration
# ============================================================================

# Patterns to remove from translations
REMOVE_PATTERNS = [
    r'Page\s+\d+\s+(?:sur|of)\s+\d+',  # Page numbers
    r'^Here is the translation[:\s]*',  # Common prefixes
    r'^Translation[:\s]*',
    r'^සිංහල පරිවර්තනය[:\s]*',
    r'^English translation[:\s]*',
    r'^Sinhala translation[:\s]*',
    r'^\*+\s*Translation\s*\*+[:\s]*',
]

# Whether to remove Pali references in square brackets [like this]
REMOVE_PALI_REFERENCES = True

# ============================================================================
# Advanced Configuration
# ============================================================================

# Enable caching of translations (experimental)
ENABLE_CACHE = False

# Cache file path
CACHE_FILE = 'translation_cache.json'

# Enable parallel translation (requires multiple API keys)
ENABLE_PARALLEL = False

# Number of parallel workers
PARALLEL_WORKERS = 2

# ============================================================================
# Section Detection Configuration
# ============================================================================

# Patterns that indicate a new section
SECTION_START_PATTERNS = [
    r'^\d+\.',  # Numbered sections (1., 2., etc.)
    r'^[A-Z][a-z]+vatthu$',  # Vatthu sections
    r'^[A-Z][a-z]+kathā$',  # Kathā sections
]

# Patterns that indicate a title
TITLE_PATTERNS = [
    r'suttaṃ$',
    r'vatthu$',
    r'kathā$',
    r'vaggapāḷi$',
]

# Maximum line length for a title (characters)
MAX_TITLE_LENGTH = 100

# ============================================================================
# Validation Configuration
# ============================================================================

# Minimum acceptable translation length (as % of original)
MIN_TRANSLATION_LENGTH_RATIO = 0.5

# Maximum acceptable translation length (as % of original)
MAX_TRANSLATION_LENGTH_RATIO = 3.0

# Warn if translation differs significantly from source length
WARN_LENGTH_DIFFERENCE = True

# ============================================================================
# Output Format Configuration
# ============================================================================

# JSON indentation (spaces)
JSON_INDENT = 2

# Ensure ASCII in JSON output (False = allow Unicode)
JSON_ENSURE_ASCII = False

# Pretty print JSON
JSON_PRETTY_PRINT = True

# ============================================================================
# Helper Functions
# ============================================================================

def get_full_pali_path():
    """Get full path to Pali source file"""
    import os
    return os.path.join(INPUT_DIR, PALI_SOURCE_FILE)

def get_full_book_path():
    """Get full path to book metadata file"""
    import os
    return os.path.join(INPUT_DIR, BOOK_METADATA_FILE)

def get_output_path(chapter_id, chapter_title):
    """Get output path for a chapter"""
    import os
    filename = f"{chapter_id}-{chapter_title}.json"
    return os.path.join(OUTPUT_DIR, filename)

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if MAX_CHUNK_SIZE > 8000:
        errors.append("MAX_CHUNK_SIZE is too large (>8000). May cause API errors.")
    
    if MIN_SECTION_SIZE >= MAX_SECTION_SIZE:
        errors.append("MIN_SECTION_SIZE must be less than MAX_SECTION_SIZE")
    
    if RATE_LIMIT_DELAY < 0.5:
        errors.append("RATE_LIMIT_DELAY is too small. May hit rate limits.")
    
    if TRANSLATION_TEMPERATURE < 0 or TRANSLATION_TEMPERATURE > 1:
        errors.append("TRANSLATION_TEMPERATURE must be between 0 and 1")
    
    return errors

# Validate on import
_validation_errors = validate_config()
if _validation_errors:
    import warnings
    for error in _validation_errors:
        warnings.warn(f"Configuration warning: {error}")

