# Book Translation Guide

This guide explains how to clean and retranslate all book.json files with accurate translations using your preferred tools.

## Overview

The system has extracted **22 book.json files** from all Buddhist text collections, cleared all English and Sinhala translations, and organized them for manual translation.

## What Was Done

### 1. Extracted and Cleaned
- **22 book.json files** from 4 collections
- **Cleared all English and Sinhala translations** (set to empty strings)
- **Cleared description and summary fields** that had poor translations
- **Kept all Pali text intact** for reference

### 2. Organized Structure
```
book_translations_for_manual_work/
├── Dīghanikāyo/
│   ├── Mahāvaggapāḷi_book.json
│   ├── Pāthikavaggapāḷi_book.json
│   └── Sīlakkhandhavaggapāḷi_book.json
├── Majjhimanikāye/
│   ├── Majjhimapaṇṇāsapāḷi_book.json
│   ├── Mūlapaṇṇāsapāḷi_book.json
│   └── Uparipaṇṇāsapāḷi_book.json
├── Saṃyuttanikāyo/
│   ├── Khandhavaggo_book.json
│   ├── Mahāvaggo_book.json
│   ├── Nidānavaggo_book.json
│   ├── Sagāthāvaggo_book.json
│   └── Saḷāyatanavaggo_book.json
├── Aṅguttaranikāyo/
│   ├── Aṭṭhakanipātapāḷi_book.json
│   ├── Catukkanipātapāḷi_book.json
│   ├── Chakkanipātapāḷi_book.json
│   ├── Dasakanipātapāḷi_book.json
│   ├── Dukanipātapāḷi_book.json
│   ├── Ekakanipātapāḷi_book.json
│   ├── Ekādasakanipātapāḷi_book.json
│   ├── Navakanipātapāḷi_book.json
│   ├── Pañcakanipātapāḷi_book.json
│   ├── Sattakanipātapāḷi_book.json
│   └── Tikanipātapāḷi_book.json
└── file_reference.json
```

## Translation Process

### Step 1: Translate the Files
1. **Open each JSON file** in the `book_translations_for_manual_work` folder
2. **Use Google Gemini** or your preferred translation tool
3. **Fill in all empty fields**:
   - `"english": ""` → Add English translation
   - `"sinhala": ""` → Add Sinhala translation
4. **Keep Pali text unchanged**

### Step 2: Apply Translations
```bash
python apply_book_translations.py
```
This will:
- Copy your translated files back to the original locations
- Create backup files (.json.backup) for safety
- Apply all 22 book translations

### Step 3: Verify Results
```bash
python extract_missing_translations.py
```
This will show if any translations are still missing.

## Fields to Translate

Each book.json contains these translation fields:

### Core Structure
- **Basket name**: `basket.name.english/sinhala`
- **Collection name**: `collection.name.english/sinhala`
- **Book name**: `nipata.name.english/sinhala` or `vagga.name.english/sinhala`
- **Title**: `title.english/sinhala`
- **Footer**: `footer.english/sinhala`
- **Description**: `description.english/sinhala`

### Chapter Metadata
- **Chapter titles**: `chapters[].title.english/sinhala`
- **Chapter descriptions**: `chapters[].description.english/sinhala`

## Translation Guidelines

### For English:
- Use standard Buddhist terminology
- Follow academic Buddhist translation conventions
- Use proper English grammar and structure

### For Sinhala:
- Use traditional Sinhala Buddhist terminology
- Follow Sri Lankan Buddhist text conventions
- Use proper Sinhala grammar and diacritics

## Benefits

This approach provides:
- **Clean slate** for accurate translations
- **Organized workflow** with clear file structure
- **Safety backups** of original files
- **Easy verification** of completion
- **Professional quality** using advanced translation tools

## Statistics

- **Collections**: 4 (Dīgha, Majjhima, Saṃyutta, Aṅguttara)
- **Books**: 22 total
- **Files created**: 22 + 1 reference file
- **Translation fields**: ~200+ fields across all books

## Next Steps

1. **Translate** all files in `book_translations_for_manual_work/`
2. **Run** `python apply_book_translations.py`
3. **Verify** with `python extract_missing_translations.py`

This will give you complete, accurate translations for all book metadata!