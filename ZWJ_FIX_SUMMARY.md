# ZWJ (Zero-Width Joiner) Issue - Fixed

## Problem

Some Sinhala translations contained **literal text `<ZWJ>`** instead of the actual Zero-Width Joiner Unicode character (U+200D).

### Example of the Issue

**Incorrect (what was in the file):**
```
සුනක්ඛත්ත ලිච්ඡවිපුත්‍ර<ZWJ>යාට
```

**Correct (what it should be):**
```
සුනක්ඛත්ත ලිච්ඡවිපුත්‍ර‍යාට
```
(Note: The ZWJ character U+200D is invisible but present between ර and ය)

## Root Cause

The AI translation model sometimes outputs `<ZWJ>` as **visible placeholder text** instead of the actual invisible Unicode character (U+200D). This happens because:

1. The ZWJ character (U+200D) is invisible, making it hard for the AI to "see"
2. The AI tries to be "helpful" by making it visible as `<ZWJ>` text
3. This breaks proper Sinhala rendering because `<ZWJ>` is just regular text, not a Unicode control character

## Impact

- **4 files affected** with 57 total occurrences:
  - `Pāthikavaggapāḷi/chapters/dn1-Pāthikasuttaṃ.json` (14 occurrences)
  - `Pāthikavaggapāḷi/chapters/dn2-Udumbarikasuttaṃ.json` (20 occurrences)
  - `Sīlakkhandhavaggapāḷi/chapters/dn2-Sāmaññaphalasuttaṃ.json` (15 occurrences)
  - `Sīlakkhandhavaggapāḷi/chapters/dn8-Mahāsīhanādasuttaṃ.json` (8 occurrences)

## Solution Applied

### 1. Immediate Fix - Batch Replacement

Created and ran `fix_zwj_literals.py` to replace all `<ZWJ>` text with actual U+200D characters:

```python
# Replace literal <ZWJ> with actual Zero-Width Joiner
fixed_content = content.replace('<ZWJ>', '\u200D')
```

**Result:** All 57 occurrences fixed across 4 files ✓

### 2. Prevention - Updated Translation Scripts

Added automatic post-processing to both translation scripts to catch this issue in future translations:

#### Updated Files:
1. **`translate_json_chapters.py`** - Added to `clean_translation()` method
2. **`verify_and_clean_translations.py`** - Added to `clean_text()` method

#### Code Added:
```python
# CRITICAL: Replace literal <ZWJ> text with actual Zero-Width Joiner (U+200D)
# Sometimes AI outputs <ZWJ> as visible text instead of the actual invisible character
text = text.replace('<ZWJ>', '\u200D')
```

This ensures that even if the AI outputs `<ZWJ>` as text, it will be automatically converted to the proper Unicode character.

## Why ZWJ is Important for Sinhala

The Zero-Width Joiner (U+200D) is **essential** for proper Sinhala conjunct rendering:

### Without ZWJ (Broken):
- `ක්ය` - consonant cluster appears disconnected
- `භාග්යවතුන්` - looks wrong

### With ZWJ (Correct):
- `ක්‍ය` - properly joined conjunct
- `භාග්‍යවතුන්` - correct rendering

### Common Sinhala Conjuncts Requiring ZWJ:
- `ක්‍ය` (kya)
- `ක්‍ර` (kra)
- `ප්‍ර` (pra)
- `ත්‍ර` (tra)
- `ශ්‍ර` (śra)
- `ග්‍ර` (gra)
- `ධ්‍ර` (dhra)
- `භ්‍ය` (bhya)

## Verification

To check if a file has this issue:

```powershell
# Search for literal <ZWJ> text
Get-Content "path/to/file.json" -Encoding UTF8 | Select-String "ZWJ"
```

To fix manually:
```powershell
python fix_zwj_literals.py
```

## Future Translations

**No action needed!** The translation scripts now automatically fix this issue during the cleaning phase. Any future translations will have `<ZWJ>` text automatically converted to the proper U+200D character.

## Technical Details

- **Unicode Character:** U+200D (Zero-Width Joiner)
- **Purpose:** Joins characters that should form ligatures or conjuncts
- **Visibility:** Invisible (zero-width)
- **Essential for:** Sinhala, Devanagari, Arabic, and other complex scripts
- **Not to be confused with:**
  - U+200B (Zero-Width Space) - should be removed
  - U+200C (Zero-Width Non-Joiner) - should be removed
  - U+FEFF (Zero-Width No-Break Space) - should be removed

## Summary

✅ **Fixed:** All 57 occurrences of `<ZWJ>` literal text replaced with proper U+200D character  
✅ **Prevented:** Translation scripts updated to automatically fix this in future  
✅ **No re-translation needed:** Existing translations are now correct  

The issue is completely resolved and won't happen again in future translations.
