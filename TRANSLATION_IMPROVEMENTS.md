# Translation Improvements Log

## Enhanced Sinhala Buddhist Terminology Translation

### Issue: Ambiguous Modern Sinhala Translations

**Problem Example:**
- Pali term: `Khaṇakicco` (from "Khaṇa" + "kicca")
- Previous translation: `ක්ෂණකාරී` (momentary)
- **Issue**: In modern Sinhala, this is ambiguous and loses the doctrinal meaning
- **Correct meaning**: "The world has a duty/task that must be done in this moment"

### Solution Implemented

Added a new rule to the translation prompts to preserve full philosophical meanings of Pali Buddhist terms rather than literal word-by-word translations.

#### Changes Made:

**1. In `translate_json_chapters.py` (Line 300-302):**
```
CRITICAL FOR SINHALA:
- IMPORTANT: Translate Pali terms with their full philosophical meaning, not literal word-by-word
  Example: "Khaṇakicco" means "has a duty/task that must be done in this moment" NOT just "momentary"
  Preserve the nuanced doctrinal meaning rather than simplified modern interpretations
```

**2. In `config.py` (Line 150-153):**
```python
8. CRITICAL: Translate Pali terms with their full philosophical meaning, not literal word-by-word
   - Example: "Khaṇakicco" = "මේ මොහොතේම සිදු කළ යුතු කර්තව්‍යය ඇති" (has a duty that must be done in this moment)
   - NOT: "ක්ෂණකාරී" (momentary) which is ambiguous and loses the doctrinal meaning
   - Preserve nuanced Buddhist doctrinal meanings rather than simplified modern interpretations
```

### Expected Improvements

With this rule, the AI translator will now:

1. **Analyze the full doctrinal context** of Pali compound words
2. **Translate the philosophical meaning** rather than just the literal words
3. **Preserve Buddhist doctrinal nuances** that might be lost in simplified translations
4. **Use appropriate Sinhala Buddhist terminology** that conveys the full meaning

### Examples of Terms That Will Benefit:

- `Khaṇakicco` → Full duty/responsibility meaning instead of just "momentary"
- `Dhammakāya` → Dhamma body (doctrinal meaning) not just "law body"
- `Cittuppāda` → Arising of intention/mind-moment, not just "mind arising"
- `Saṅkhāra` → Volitional formations (full doctrinal meaning) not just "formations"
- `Paṭiccasamuppāda` → Dependent origination (full teaching) not just "co-arising"

### How to Use:

Simply run the translation as normal. The AI will now:
- Recognize when a Pali term has deeper philosophical meaning
- Consider the Buddhist doctrinal context
- Provide translations that preserve the full teaching

### Re-translating Existing Sections:

If you want to re-translate sections that have ambiguous terms:

1. **Option 1: Delete existing translations**
   - Delete the `"english"` or `"sinhala"` fields from the JSON
   - Run the translator again - it will only translate missing sections

2. **Option 2: Manual spot-check**
   - Review existing translations for ambiguous terms
   - Use your Buddhist knowledge to identify issues
   - Selectively re-translate those specific sections

### Common Pali Compound Patterns to Watch:

1. **-kicca** (duty, task, function) - not just action
2. **-gāmī** (leading to, going towards) - with doctrinal goal in mind
3. **-samādhi** (concentration, but with specific qualities)
4. **-paññā** (wisdom, but with understanding of what kind)
5. **-bhāvanā** (development, cultivation - with specific practice context)

### Notes:

- This rule does NOT remove any existing translation rules
- All other requirements (ZWJ, Unicode, etc.) remain intact
- The AI will now make more informed decisions about Buddhist terminology
- Traditional Sinhala Buddhist terms are preferred over modern simplified versions

