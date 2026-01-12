# Duplicate Sections Report

## Summary

Found **3 files** with duplicate section entries in the database.

## Duplicate Details

### 1. Majjhima Nikāya - mn.3.1-Devadahavaggo.json

- **File**: `Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters/mn.3.1-Devadahavaggo.json`
- **Chapter ID**: `mn.3.1`
- **Duplicate Section**: Section **2** appears **2 times**
- **Collection**: Majjhima Nikāya
- **Book**: Uparipaṇṇāsapāḷi

### 2. Saṃyutta Nikāya - sn.2.1-Nidānasaṃyuttaṃ.json

- **File**: `Saṃyuttanikāyo/Nidānavaggo/chapters/sn.2.1-Nidānasaṃyuttaṃ.json`
- **Chapter ID**: `sn.2.1`
- **Duplicate Section**: Section **73** appears **3 times**
- **Collection**: Saṃyutta Nikāya
- **Book**: Nidānavaggo

### 3. Saṃyutta Nikāya - sn.4.1-Saḷāyatanasaṃyuttaṃ.json

- **File**: `Saṃyuttanikāyo/Saḷāyatanavaggo/chapters/sn.4.1-Saḷāyatanasaṃyuttaṃ.json`
- **Chapter ID**: `sn.4.1`
- **Duplicate Section**: Section **1** appears **2 times**
- **Collection**: Saṃyutta Nikāya
- **Book**: Saḷāyatanavaggo

## How to Fix

### Option 1: Fix in JSON Files (Recommended)

1. Run the fix script:
   ```bash
   python fix_duplicate_sections.py
   ```

2. This will:
   - Create backups of the original files (`.json.backup`)
   - Remove duplicate sections from the JSON files
   - Keep only the first occurrence of each section

3. After fixing, re-import the corrected files to Turso

### Option 2: Fix Directly in Database

1. Run the database cleanup script:
   ```bash
   python remove_duplicate_sections_from_db.py
   ```

2. This will:
   - Show a dry run first (no changes)
   - Ask for confirmation
   - Remove duplicate entries from the database
   - Keep the section with the lowest ID (first inserted)

## Verification

After fixing, run the check again:
```bash
python check_sections_simple.py
```

This should show:
- Files with duplicate sections: **0**
- All duplicates resolved ✅

## Root Cause

The duplicates were likely caused by:
1. Running the import script multiple times on the same data
2. The import script using `INSERT` instead of `INSERT OR REPLACE` for sections
3. Not checking for existing sections before inserting

## Prevention

To prevent this in the future:
1. Always use `INSERT OR REPLACE` or check for existing records
2. Add a unique constraint on `(chapter_id, section_number)` in the database schema
3. Run verification checks after imports

## Database Schema Recommendation

Add this constraint to prevent future duplicates:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_sections_unique 
ON sections(chapter_id, section_number);
```

This will ensure that each section number within a chapter can only exist once.
