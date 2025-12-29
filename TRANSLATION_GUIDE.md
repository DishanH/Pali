# Translation Workflow Guide

This guide explains how to efficiently translate missing Pali terms using Google Translate's free quota.

## 📊 Current Status

After running the extraction script, we found:
- **1,603 missing English translations**
- **1,603 missing Sinhala translations**
- **Total**: 3,206 translations needed

## 🚀 Quick Start

### 1. Extract Missing Translations
```bash
python extract_missing_translations.py
```

This creates the `missing_translations/` directory with organized files.

### 2. Install Translation Dependencies
```bash
pip install -r translation_requirements.txt
```

### 3. Check Progress
```bash
python batch_translate.py english --mode progress
python batch_translate.py sinhala --mode progress
```

### 4. Translate in Batches (Recommended)
```bash
# Translate first 20 English terms
python batch_translate.py english --mode batch --batch-size 20 --start-row 0

# Next day, translate next 20 terms
python batch_translate.py english --mode batch --batch-size 20 --start-row 20

# Continue daily...
```

### 5. Apply Translations Back to Source Files
```bash
python apply_translations.py
```

## 📋 Translation Strategies

### Strategy 1: Daily Batch Translation (Recommended)
- **Google Free Quota**: 20 requests/day
- **Time needed**: ~80 days for English + 80 days for Sinhala = 160 days total
- **Effort**: 5-10 minutes per day

```bash
# Day 1
python batch_translate.py english --batch-size 20 --start-row 0

# Day 2  
python batch_translate.py english --batch-size 20 --start-row 20

# Day 3
python batch_translate.py english --batch-size 20 --start-row 40

# Continue...
```

### Strategy 2: Interactive Translation
- **Best for**: Quality control and manual review
- **Usage**: Review auto-translations and make corrections

```bash
python batch_translate.py english --mode interactive
```

### Strategy 3: Mixed Approach
1. Use batch mode for bulk translation
2. Use interactive mode for important/frequent terms
3. Manually edit CSV files for corrections

## 📁 File Structure

```
missing_translations/
├── missing_english_translations.csv     # Main English translation file
├── missing_sinhala_translations.csv     # Main Sinhala translation file
├── missing_english_translations.json    # JSON format (backup)
├── missing_sinhala_translations.json    # JSON format (backup)
├── missing_english_batch_20.txt         # Daily batch reference
├── missing_sinhala_batch_20.txt         # Daily batch reference
└── translation_summary.md               # Statistics and overview
```

## 🎯 Priority Terms

The extraction script prioritizes terms by frequency:
1. **Most frequent terms first** (appear in multiple contexts)
2. **Alphabetical order** for same frequency

Top missing terms include:
- `Dutiyavaggo` (appears 11 times)
- `Bhikkhusuttaṃ` (appears 10 times)
- `Paṭhamavaggo` (appears 10 times)

## 📝 Manual Editing

You can also manually edit the CSV files:

1. Open `missing_translations/missing_english_translations.csv`
2. Fill in the "English Translation" column
3. Save the file
4. Run `python apply_translations.py`

## 🔄 Workflow Commands

### Check what needs translation
```bash
python batch_translate.py english --mode progress
```

### Translate next batch
```bash
# Find current progress first, then:
python batch_translate.py english --batch-size 20 --start-row [CURRENT_ROW]
```

### Apply completed translations
```bash
python apply_translations.py
```

### Re-extract after updates (if needed)
```bash
python extract_missing_translations.py
```

## 💡 Tips for Efficiency

### 1. Focus on High-Frequency Terms
- Start with terms that appear in multiple contexts
- These give maximum impact per translation

### 2. Use Context Information
- The CSV files show where each term is used
- Use context to choose better translations

### 3. Batch Similar Terms
- Group related terms (e.g., all "vagga" names)
- Maintain consistency in translation style

### 4. Quality Control
- Use interactive mode for important terms
- Review auto-translations before applying

### 5. Track Progress
- Run progress check regularly
- Celebrate milestones (every 100 translations)

## 🚨 Rate Limiting

Google Translate free tier limits:
- **20 requests per day**
- **Resets at midnight UTC**
- **No monthly rollover**

If you hit the limit:
- Wait until next day
- Use manual translation for urgent terms
- Consider Google Cloud Translation API for higher limits

## 🔧 Troubleshooting

### Translation Errors
```bash
# Check for network issues
ping translate.googleapis.com

# Try smaller batch size
python batch_translate.py english --batch-size 10
```

### CSV File Issues
- Ensure proper UTF-8 encoding
- Don't edit while scripts are running
- Keep backups of completed translations

### Missing Dependencies
```bash
pip install --upgrade googletrans==4.0.0rc1
```

## 📈 Progress Tracking

Create a simple progress log:

```
# translation_log.txt
Day 1: English 0-19 (20 terms) ✓
Day 2: English 20-39 (20 terms) ✓  
Day 3: English 40-59 (20 terms) ✓
...
```

## 🎉 Completion

Once all translations are complete:

1. Run final application: `python apply_translations.py`
2. Verify with: `python extract_missing_translations.py` (should show 0 missing)
3. Test database import: `python import_to_turso_updated.py`
4. Archive translation files for future reference

## 📞 Support

If you encounter issues:
1. Check the error messages carefully
2. Verify file permissions and encoding
3. Ensure stable internet connection
4. Try smaller batch sizes if timeouts occur

---

**Estimated Timeline**: 160 days at 20 translations per day
**Daily Effort**: 5-10 minutes
**Total Impact**: Complete multilingual Buddhist text database