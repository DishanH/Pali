# Bulk Footer Translation Guide

This guide explains how to use the bulk footer translation system to efficiently translate all missing Pali footer texts in the Buddhist text collections.

## Overview

The system found **92 missing footer translations** across 22 books and 291 chapters. These are typically chapter/section ending formulas that indicate the position of the text within the collection.

## Files Created

### 1. Core Scripts
- `extract_missing_footers.py` - Extracts all missing footer translations
- `chunk_footer_translations.py` - Splits translations into manageable chunks
- `merge_completed_footer_chunks.py` - Merges translated chunks back together
- `apply_bulk_footer_translations.py` - Applies translations to source files

### 2. Generated Files
- `bulk_footer_translations.json` - Main file with all 92 footer terms
- `footer_chunk_01.json` - First 50 footer terms for translation
- `footer_chunk_02.json` - Remaining 42 footer terms for translation

## Translation Process

### Step 1: Extract Missing Footers (Already Done)
```bash
python extract_missing_footers.py
```
This creates `bulk_footer_translations.json` with 92 missing footer terms.

### Step 2: Split into Chunks (Already Done)
```bash
python chunk_footer_translations.py
```
This creates 2 chunk files for easier translation.

### Step 3: Translate the Chunks
You need to translate the footer terms in both chunk files:
- `footer_chunk_01.json` (50 terms)
- `footer_chunk_02.json` (42 terms)

**Translation Method:**
1. Use Google Gemini, ChatGPT, or your preferred translation tool
2. Fill in the `"english"` and `"sinhala"` fields for each term
3. Keep the Pali text and context information unchanged

### Step 4: Merge Translated Chunks
```bash
python merge_completed_footer_chunks.py
```
This merges your translated chunks back into `bulk_footer_translations.json`.

### Step 5: Apply Translations
```bash
python apply_bulk_footer_translations.py
```
This applies all translations to the source JSON files.

## Footer Types Found

The footers are typically chapter/section endings that follow patterns like:

### Common Patterns:
- `[Collection]saṃyuttaṃ [number]maṃ.` - "The [Collection] Connected Discourses, [ordinal number]."
- `[Book]nipātapāḷi [number]maṃ.` - "The [Book] Section, [ordinal number]."
- `[Section]vaggo [number]mo.` - "The [Section] Chapter, [ordinal number]."

### Examples:
- `Sotāpattisaṃyuttaṃ ekādasamaṃ.` → "The Stream-Entry Connected Discourses, the eleventh."
- `Saccasaṃyuttaṃ dvādasamaṃ.` → "The Truth Connected Discourses, the twelfth."
- `Bojjhaṅgasaṃyuttaṃ dutiyaṃ.` → "The Factors of Enlightenment Connected Discourses, the second."

## Translation Guidelines

### For English:
- Use standard Buddhist terminology
- Follow the pattern: "The [Topic] Connected Discourses, the [ordinal number]."
- Use proper ordinal numbers (first, second, third, etc.)

### For Sinhala:
- Use proper Sinhala Buddhist terminology
- Follow traditional Sinhala Buddhist text conventions
- Use appropriate Sinhala ordinal numbers

### Ordinal Numbers Reference:
- paṭhamaṃ/ekādasamaṃ = first/eleventh
- dutiyaṃ = second  
- tatiyaṃ = third
- catutthaṃ = fourth
- pañcamaṃ = fifth
- chaṭṭhaṃ = sixth
- sattamaṃ = seventh
- aṭṭhamaṃ = eighth
- navamaṃ = ninth
- dasamaṃ = tenth
- dvādasamaṃ = twelfth

## Statistics

- **Total footer terms**: 92
- **Books scanned**: 22
- **Chapters scanned**: 291
- **Footers found**: 310
- **Missing English**: 92
- **Missing Sinhala**: 92

## Benefits

This bulk translation approach:
- Reduces translation time from weeks to hours
- Ensures consistency across all footer translations
- Allows use of advanced translation tools like Google Gemini
- Provides context for each footer term
- Maintains proper Buddhist terminology

## Next Steps

1. Translate the terms in `footer_chunk_01.json` and `footer_chunk_02.json`
2. Run `python merge_completed_footer_chunks.py`
3. Run `python apply_bulk_footer_translations.py`
4. Verify the results with `python extract_missing_footers.py`

The system will then show 0 missing footer translations across all collections!