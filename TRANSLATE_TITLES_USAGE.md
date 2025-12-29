# Section Title & Footer Translator - Usage Guide

## Overview
This script translates missing Pali section titles and footers to English and Sinhala in JSON chapter files.

## Features
- ✅ Single directory processing
- ✅ **Recursive directory processing** (NEW!)
- ✅ Resume from specific file and section
- ✅ Automatic progress saving
- ✅ Foreign character validation for Sinhala
- ✅ Rate limit and quota handling

## Usage Modes

### Mode 1: Single Chapters Directory
Process files in a single `chapters` directory.

**Example:**
```
Enter directory path: Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters
Enter file pattern: mn*.json
```

This will process only files in that specific chapters directory.

### Mode 2: Recursive Parent Directory (NEW!)
Process all `chapters` subdirectories within a parent directory.

**Example:**
```
Enter directory path: Majjhimanikāye
Enter file pattern: mn*.json
```

This will automatically find and process:
- `Majjhimanikāye/Mūlapaṇṇāsapāḷi/chapters/mn*.json`
- `Majjhimanikāye/Majjhimapaṇṇāsapāḷi/chapters/mn*.json`
- `Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters/mn*.json`

The script will:
1. Search for all subdirectories containing a `chapters` folder
2. Display all found directories
3. Ask for confirmation to search recursively
4. Process all matching JSON files in order

## File Patterns

### Common Patterns
- `*.json` - All JSON files
- `mn*.json` - Majjhima Nikāya files (mn.1.1-*, mn.1.2-*, etc.)
- `dn*.json` - Dīgha Nikāya files
- `sn*.json` - Saṃyutta Nikāya files
- `an*.json` - Aṅguttara Nikāya files
- `vv*.json` - Vimānavatthu files

### Specific Patterns
- `mn.3.*.json` - Only Uparipaṇṇāsapāḷi files
- `mn.1.*.json` - Only Mūlapaṇṇāsapāḷi files
- `mn.2.*.json` - Only Majjhimapaṇṇāsapāḷi files

## Example Workflows

### Workflow 1: Process All Majjhima Nikāya Files
```
Enter directory path: Majjhimanikāye
Found subdirectories with 'chapters' folders. Search recursively? (y/n, default: y): y
Enter file pattern: mn*.json
```

Result: Processes all mn*.json files across all three paṇṇāsa collections.

### Workflow 2: Process Only Uparipaṇṇāsapāḷi
```
Enter directory path: Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters
Enter file pattern: *.json
```

Result: Processes only files in Uparipaṇṇāsapāḷi chapters directory.

### Workflow 3: Process Specific Vaggo Pattern
```
Enter directory path: Majjhimanikāye
Search recursively? (y): y
Enter file pattern: mn.3.*.json
```

Result: Processes only Uparipaṇṇāsapāḷi files (mn.3.1, mn.3.2, etc.).

## Resume Functionality

If the script stops due to quota limits or errors, you can resume:

```
Resume from file: mn.3.3-Suññatavaggo.json
Resume from section number: 5
```

This will:
1. Skip all files before `mn.3.3-Suññatavaggo.json`
2. Start processing from section 5 of that file
3. Continue with all remaining files

## Directory Structure Example

```
Majjhimanikāye/
├── Mūlapaṇṇāsapāḷi/
│   └── chapters/
│       ├── mn.1.1-Mūlapariyāyavaggo.json
│       ├── mn.1.2-Sīhanādavaggo.json
│       └── ...
├── Majjhimapaṇṇāsapāḷi/
│   └── chapters/
│       ├── mn.2.1-Gahapativaggo.json
│       └── ...
└── Uparipaṇṇāsapāḷi/
    └── chapters/
        ├── mn.3.1-Devadahavaggo.json
        ├── mn.3.2-Anupadavaggo.json
        └── ...
```

When you provide `Majjhimanikāye` as the directory, the script will:
1. Find all three `chapters` subdirectories
2. Collect all matching JSON files
3. Process them in alphabetical order

## What Gets Translated

For each JSON file, the script translates:

1. **Section Titles** (if missing):
   - `paliTitle` → `englishTitle`
   - `paliTitle` → `sinhalaTitle`

2. **Footer** (if missing):
   - `footer.pali` → `footer.english`
   - `footer.pali` → `footer.sinhala`

## Progress Tracking

The script shows:
- Current file being processed
- Section progress (e.g., [5/20])
- Translation status for each section
- Total statistics at the end

Example output:
```
🔍 Searching for 'chapters' directories in: Majjhimanikāye
Found 3 chapters directories:
  📁 Majjhimapaṇṇāsapāḷi/chapters
  📁 Mūlapaṇṇāsapāḷi/chapters
  📁 Uparipaṇṇāsapāḷi/chapters
  ✓ 5 files in Majjhimapaṇṇāsapāḷi/chapters
  ✓ 5 files in Mūlapaṇṇāsapāḷi/chapters
  ✓ 5 files in Uparipaṇṇāsapāḷi/chapters

📚 Total: 15 JSON files to process

============================================================
Processing: mn.1.1-Mūlapariyāyavaggo.json
============================================================

[1/20] Section 1: Mūlapariyāyavaggo
  → English title... ✓ The Root Sequence
  → Sinhala title... ✓ මූල පරියාය වර්ගය
```

## Tips

1. **Use specific patterns** when possible to avoid processing unnecessary files
2. **Start with a small test** on one directory before running on entire collections
3. **Monitor quota usage** - the script will automatically stop and tell you how to resume
4. **Check logs** in `translator.log` for detailed information
5. **Backup your files** before running large batch operations

## Configuration

Edit `config.py` to customize:
- Model name
- Rate limit delays
- Retry settings
- Logging options








