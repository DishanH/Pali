# Fix Duplicate Sections - Complete Workflow

## Overview

This guide walks you through fixing duplicate section entries in your Turso database.

## Problem Summary

- **3 files** have duplicate section entries
- **Total duplicates**: 4 duplicate entries (some sections appear 2-3 times)
- These were likely created during multiple import runs

## Step-by-Step Fix

### Step 1: Review the Duplicates

Check what duplicates exist:

```bash
python check_sections_simple.py
```

This will show:
- ✅ Files with duplicate sections: 3
- Details saved to `file_section_check_report.json`

### Step 2: Remove Duplicates from Database

Run the database cleanup script:

```bash
python remove_duplicate_sections_from_db.py
```

**What it does:**
1. Connects to your Turso database
2. Finds all duplicate sections
3. Shows a dry run (no changes)
4. Asks for confirmation
5. Removes duplicates (keeps the first occurrence)
6. Verifies no duplicates remain

**Example output:**
```
Found 3 duplicate section entries:

Chapter: mn.3.1, Section: 2
  Keeping ID: 12345
  Removing IDs: [12346]

Chapter: sn.2.1, Section: 73
  Keeping ID: 23456
  Removing IDs: [23457, 23458]

Chapter: sn.4.1, Section: 1
  Keeping ID: 34567
  Removing IDs: [34568]

Proceed with removing duplicates? (yes/no):
```

Type `yes` to proceed.

### Step 3: Add Unique Constraint (Prevent Future Duplicates)

After removing duplicates, add a constraint to prevent them from happening again:

```bash
python add_unique_constraint.py
```

**What it does:**
- Adds a unique index on `(chapter_id, section_number)`
- Prevents duplicate section numbers within the same chapter
- Future import attempts with duplicates will fail with an error

### Step 4: Verify the Fix

Run the check again to confirm:

```bash
python check_sections_simple.py
```

Should show:
```
Files with duplicate sections: 0
✅ All duplicates resolved!
```

### Step 5: Fix Source JSON Files (Optional but Recommended)

To keep your JSON files in sync with the database:

```bash
python fix_duplicate_sections.py
```

**What it does:**
1. Creates backups (`.json.backup`)
2. Removes duplicates from the 3 JSON files
3. Keeps only the first occurrence

**Files that will be fixed:**
- `Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters/mn.3.1-Devadahavaggo.json`
- `Saṃyuttanikāyo/Nidānavaggo/chapters/sn.2.1-Nidānasaṃyuttaṃ.json`
- `Saṃyuttanikāyo/Saḷāyatanavaggo/chapters/sn.4.1-Saḷāyatanasaṃyuttaṃ.json`

## Quick Reference

### All Scripts

| Script | Purpose |
|--------|---------|
| `check_sections_simple.py` | Check for duplicates and missing sections in JSON files |
| `remove_duplicate_sections_from_db.py` | Remove duplicates from Turso database |
| `add_unique_constraint.py` | Add constraint to prevent future duplicates |
| `fix_duplicate_sections.py` | Fix duplicate sections in JSON files |

### Execution Order

```bash
# 1. Check what's wrong
python check_sections_simple.py

# 2. Fix database
python remove_duplicate_sections_from_db.py

# 3. Prevent future duplicates
python add_unique_constraint.py

# 4. Fix source files (optional)
python fix_duplicate_sections.py

# 5. Verify everything is fixed
python check_sections_simple.py
```

## What About Missing Sections?

The check also found **52 files with missing sections**. These are NOT duplicates - they are gaps in section numbering (e.g., sections 1, 2, 10, 11 - missing 3-9).

**These are likely intentional** because:
- Many chapters use "peyyāla" (repetition) sections
- The PDF source may have abbreviated repetitive content
- Section numbers may skip to indicate omitted repetitions

**Action**: Review these manually if needed, but they don't need automatic fixing.

## Troubleshooting

### Error: "UNIQUE constraint failed"

This means duplicates still exist. Run:
```bash
python remove_duplicate_sections_from_db.py
```

### Error: "Module not found: libsql_experimental"

Install the required package:
```bash
pip install libsql-experimental
```

### Error: "Environment variables not set"

Make sure your `.env` file contains:
```
TURSO_DB_URL=libsql://your-database.turso.io
TURSO_AUTH_TOKEN=your_token_here
```

## Prevention Tips

1. **Always use the unique constraint** - Run `add_unique_constraint.py` after setting up the database
2. **Check before importing** - Run `check_sections_simple.py` before and after imports
3. **Use INSERT OR REPLACE** - Update import scripts to use `INSERT OR REPLACE` instead of `INSERT`
4. **Backup before imports** - Always backup your database before bulk imports

## Summary

✅ **3 duplicate entries** found and can be fixed
✅ **Scripts ready** to fix both database and JSON files
✅ **Prevention mechanism** available (unique constraint)
⚠️ **52 files with missing sections** - likely intentional, review manually if needed

Run the scripts in order and your database will be clean!
