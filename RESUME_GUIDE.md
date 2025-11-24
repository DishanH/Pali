# Resume Translation Guide

## Overview

The translation system now supports **automatic incremental saving** and **resume functionality**. If a translation is interrupted (by error, rate limit, or manual stop), you can resume from where it left off.

## Key Features

### 1. Incremental Progress Saving
- **Automatic**: Progress is saved after each section is translated
- **Partial files**: Marked with `_partial: true` in the JSON
- **Metadata**: Includes `_completed_sections` and `_total_sections`
- **Atomic writes**: Uses temporary files to prevent corruption

### 2. Error Handling
- **Retry logic**: Automatically retries failed API calls (up to 3 times)
- **Exponential backoff**: Wait times increase with each retry (2s, 4s, 8s)
- **Finish reason 8**: Handles API blocking errors (safety filters, recitation blocks)
- **Rate limit handling**: Respects API rate limits with configurable delays

### 3. Resume Detection
The resume script automatically detects:
- **Partial files**: JSON files with `_partial: true` marker
- **Log analysis**: Checks translator.log for last attempted chapter
- **Section count**: Knows exactly where to resume from

## How to Use

### Starting a New Translation

```bash
python translator.py
```

### Resuming After Interruption

```bash
python resume_translation.py
```

The script will:
1. Scan for partial translation files
2. Show you what was in progress
3. Ask if you want to resume
4. Continue from the last completed section

### Example Output

```
============================================================
🔄 Resume Translation
============================================================

📁 Found 1 partial translation(s):
   1. dn6: 17/34 sections completed

📖 Resuming:
   Chapter: dn6
   Last completed section: 17

❓ Resume from section 18? (yes/no): yes
```

## Error Scenarios

### 1. API Blocking (finish_reason 8)

**What it means**: The API blocked the response due to:
- Safety filters
- Recitation detection (copyrighted content)
- Other content policy violations

**What happens**:
- System automatically retries with exponential backoff
- Waits 2s, then 4s, then 8s between retries
- After 3 failed attempts, saves progress and exits
- You can resume later with `resume_translation.py`

**Example**:
```
[18/34] Translating section 181...
  → Sinhala translation (435 chars)...
  ⚠ Response blocked (reason 8), retrying in 2s...
  ⚠ Response blocked (reason 8), retrying in 4s...
  ⚠ Response blocked (reason 8), retrying in 8s...
ERROR: Translation blocked by API after 3 retries

💡 Progress has been saved. You can try resuming again with:
   python resume_translation.py
```

### 2. Rate Limit Exceeded (429)

**What it means**: Too many API requests in a short time

**What happens**:
- Verification step may fail (non-critical)
- Primary translation continues
- System respects rate limit delays

**Solution**:
- Wait a few minutes
- Resume with `resume_translation.py`
- Consider increasing `RATE_LIMIT_DELAY` in config.py

### 3. Network Error

**What happens**:
- Progress saved up to last completed section
- Error logged to translator.log

**Solution**:
- Check internet connection
- Resume with `resume_translation.py`

## File Structure

### Partial Translation File

```json
{
  "id": "dn6",
  "title": {
    "pali": "Pāsādikasuttaṃ",
    "english": "The Delightful Discourse",
    "sinhala": "පාසාදික සූත්‍රය"
  },
  "sections": [
    {
      "number": 1,
      "pali": "...",
      "english": "...",
      "sinhala": "..."
    }
  ],
  "_partial": true,
  "_completed_sections": 17,
  "_total_sections": 34
}
```

### Final Translation File

The `_partial`, `_completed_sections`, and `_total_sections` fields are removed when the chapter is complete.

## Configuration

Edit `config.py` to adjust:

```python
# Retry and delay settings
RATE_LIMIT_DELAY = 2  # Seconds between API calls
MAX_RETRIES = 3       # Maximum retry attempts

# Model settings
MODEL_NAME = 'gemini-2.0-flash'
ENABLE_VERIFICATION = True
```

## Troubleshooting

### Resume script says "No interrupted translations found"

**Possible causes**:
1. No partial files exist (check `Pāthikavaggapāḷi/chapters/`)
2. Log file is empty or missing (check `translator.log`)

**Solution**:
- Start a new translation with `python translator.py`
- Check if files were saved in the correct directory

### Resume starts from section 1 instead of last section

**Possible causes**:
1. Partial file doesn't have `_completed_sections` metadata
2. File was created before incremental saving was implemented

**Solution**:
- Check the partial JSON file manually
- Count sections and note the last completed one
- Manually edit the file to add `_partial: true` and `_completed_sections: X`

### Translation keeps getting blocked (finish_reason 8)

**Possible causes**:
1. Content triggers safety filters
2. Text resembles copyrighted material
3. API policy changes

**Solutions**:
1. Wait 10-15 minutes and retry
2. Try a different model (edit `MODEL_NAME` in config.py)
3. Contact Google AI support if persistent
4. Check if the Pali text has unusual characters or formatting

## Best Practices

1. **Monitor progress**: Watch the console output for warnings
2. **Check logs**: Review `translator.log` for detailed error information
3. **Backup files**: Keep backups of completed chapters
4. **API limits**: Be aware of your API quota and rate limits
5. **Resume promptly**: If interrupted, resume within a few hours while log is fresh

## Technical Details

### Incremental Saving Logic

1. After each section is translated:
   - Create temporary file: `{chapter}.json.partial`
   - Write complete chapter data with `_partial: true`
   - Atomically rename to `{chapter}.json`
   - Log progress

2. On error:
   - Last saved state is preserved
   - Can resume from `_completed_sections`

### Resume Detection Logic

1. Scan `chapters/` directory for JSON files
2. Load each file and check for `_partial: true`
3. If found, extract `_completed_sections` and `_total_sections`
4. If no partial files, check `translator.log` for last attempted chapter
5. Present options to user

### Error Recovery

1. API call fails
2. Check error type:
   - `finish_reason` error → retry with backoff
   - Rate limit (429) → log warning, continue
   - Network error → save and exit
3. After max retries → save progress and exit
4. User can resume later

## Support

If you encounter issues:

1. Check `translator.log` for detailed error messages
2. Verify API key is valid and has quota
3. Check network connectivity
4. Review the error scenarios above
5. Try resuming after a short wait

## Changes Made

### `translator.py`
- Added `output_path` parameter to `translate_chapter()`
- Implemented incremental saving after each section
- Added retry logic with exponential backoff
- Enhanced error handling for finish_reason 8
- Added `_partial`, `_completed_sections`, `_total_sections` metadata

### `resume_translation.py`
- Rewrote `find_partial_translations()` to scan for partial files
- Added `find_last_attempted_chapter()` to check logs
- Enhanced user interface with better progress reporting
- Supports multiple partial files (user can choose)
- Passes `output_path` to `translate_chapter()`

## Version History

- **v1.1** (2025-11-07): Added incremental saving and resume functionality
- **v1.0** (2025-11-05): Initial translator implementation








