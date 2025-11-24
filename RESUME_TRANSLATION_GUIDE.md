# 🔄 Resume Translation Guide

## Problem: Translation Interrupted

If your translation gets interrupted (power outage, API limit, manual stop, etc.), you don't want to start from the beginning and waste time/money re-translating sections you already completed.

## Current Situation

**Before these updates:**
- ❌ Restarting would translate everything from scratch
- ❌ Would overwrite partially completed work
- ❌ No way to continue from where you left off

**After these updates:**
- ✅ Can resume from last completed section
- ✅ Skips already-translated sections
- ✅ Continues where it left off

## How to Resume

### Method 1: Automatic Resume Script ⭐ (Recommended)

```bash
python resume_translation.py
```

**What it does:**
1. 📖 Reads the log file to find what you were translating
2. 🔍 Identifies the last completed section
3. ❓ Asks if you want to resume
4. 🚀 Continues from where you left off

**Example output:**
```
🔄 Resume Translation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 Last translation:
   Chapter: dn3
   Last completed section: 26

❓ Resume from section 27? (yes/no): yes

🚀 Resuming translation from section 27...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 RESUMING from section 27/31

[27/31] Translating section 27...
  → English translation (1234 chars)... ✓ (2100 chars)
  → Sinhala translation (1234 chars)... ✓ (1800 chars)
```

### Method 2: Manual Resume (Advanced)

If you know exactly which chapter and section to resume from:

```python
# In your own script or Python shell
from translator import PaliTranslator

translator = PaliTranslator(api_key="your-key")

# Resume from section 26 (will start at section 27)
chapter_data = translator.translate_chapter(
    chapter_text,
    chapter_id="dn3",
    chapter_title="Cakkavattisuttaṃ",
    resume_from=26  # Skip first 26 sections
)
```

## When to Resume vs Start Fresh

### Resume When:
- ✅ Translation was interrupted mid-chapter
- ✅ You hit API rate limits
- ✅ Power/network failure
- ✅ Accidentally closed terminal
- ✅ Want to save time and API calls

### Start Fresh When:
- ✅ Starting a new chapter
- ✅ Previous translation had errors
- ✅ Changed translation settings/prompts
- ✅ Want to re-translate for better quality

## How It Works

### 1. Section Tracking

The translator logs every section it completes:
```
2025-11-04 16:21:04 - INFO - Translating section 26/31
2025-11-04 16:21:04 - INFO - Translating 2451 characters to English
2025-11-04 16:21:39 - INFO - Translation completed: 3393 characters
2025-11-04 16:21:41 - INFO - Translating 2451 characters to Sinhala
```

### 2. Resume Detection

`resume_translation.py` reads the log and finds:
- Which chapter you were translating
- Last section number completed
- Total sections in the chapter

### 3. Skip & Continue

When resuming with `resume_from=26`:
```python
for i, section in enumerate(sections, 1):
    if i <= resume_from:  # Skip sections 1-26
        continue
    
    # Translate section 27, 28, 29, etc.
    translate_section(section)
```

## Important Notes

### ⚠️ Limitations

1. **Partial sections are lost**
   - If section 27 was halfway done, it will restart section 27
   - Only *completed* sections are skipped

2. **Same chapter only**
   - Resume only works within the same chapter
   - Can't resume across different chapters

3. **Requires log file**
   - If `translator.log` is deleted, can't auto-detect progress
   - You'd need to manually specify section number

### ✅ What's Preserved

- ✅ Already completed translations
- ✅ Output JSON file structure
- ✅ Translation quality and consistency

## Check Current Progress

Before deciding to resume, check where you are:

```bash
# Quick status check
python check_status.py
```

**Shows:**
- Current section (e.g., 26/31)
- Last activity time
- Whether it's still running

## Complete Workflow

### If Translation is Running:
1. Check progress: `python check_status.py`
2. If active (< 2 min idle): **Wait for it to finish**
3. If stuck (> 5 min idle): **Stop and resume**

### If Translation Stopped/Crashed:
1. Check what was running: `python check_status.py`
2. Resume: `python resume_translation.py`
3. Or start fresh: `python translator.py`

### If Starting New Chapter:
1. Use regular translator: `python translator.py`
2. Select chapter number
3. Let it complete

## Examples

### Example 1: Power Outage Mid-Translation

**Before outage:**
```
[26/48] Translating section 26...
  → English translation... ✓
  → Sinhala translation... [POWER OFF]
```

**After power restored:**
```bash
$ python resume_translation.py

📖 Last translation:
   Chapter: dn1  
   Last completed section: 26

❓ Resume from section 27? yes

🔄 RESUMING from section 27/48
[27/48] Translating section 27...
```

### Example 2: Hit API Rate Limit

**Error occurred:**
```
[15/31] Translating section 15...
ERROR: Rate limit exceeded
```

**Actions:**
1. Increase `RATE_LIMIT_DELAY` in `config.py`
2. Wait a few minutes
3. Resume: `python resume_translation.py`

### Example 3: Accidentally Closed Terminal

**What happened:**
```
[40/48] Translating section 40...
  → English translation... ✓
  [Ctrl+C pressed or window closed]
```

**Resume:**
```bash
python resume_translation.py
# Will continue from section 41
```

## Saving Progress (Automatic)

The translator saves the entire chapter JSON only at the end. However:
- ✅ Log file tracks progress continuously
- ✅ Can resume based on log entries
- ❌ Partial translations not saved (only completed sections)

## Tips for Long Translations

1. **Monitor regularly:**
   ```bash
   python check_status.py  # Every 10-15 minutes
   ```

2. **Use screen/tmux (Linux) or keep terminal open (Windows):**
   - Prevents accidental closure
   - Continues if you disconnect

3. **Set reasonable rate limits:**
   ```python
   RATE_LIMIT_DELAY = 2  # Safe default
   ```

4. **Translate in smaller batches:**
   - Do 1-2 chapters at a time
   - Don't queue up all 10 chapters

5. **Check output files periodically:**
   ```bash
   ls -lh Pāthikavaggapāḷi\chapters\
   ```

## Troubleshooting

### "Could not determine what was being translated"

**Cause:** No recent activity in log file  
**Solution:** Use regular translator and select chapter manually

### Resume script shows wrong chapter

**Cause:** Log file has multiple translation sessions  
**Solution:** Check `translator.log` to verify which chapter was actually running

### Resumed translation seems to restart from beginning

**Cause:** `resume_from` parameter not passed correctly  
**Solution:** Check the resume script output, should show "RESUMING from section X"

## FAQ

**Q: Does resume cost API calls?**  
A: Only for sections NOT yet translated. Skipped sections are free!

**Q: Can I resume if I changed the model?**  
A: Yes! Model changes don't affect resume functionality.

**Q: What if I want to re-translate some sections?**  
A: Set `resume_from` to an earlier section number, or start fresh.

**Q: Is the output file overwritten on resume?**  
A: Yes, the final JSON is written at the end with all sections.

**Q: Can I pause and resume multiple times?**  
A: Yes! Resume as many times as needed.

---

## Quick Reference

| Scenario | Command |
|----------|---------|
| Check if still running | `python check_status.py` |
| Resume interrupted translation | `python resume_translation.py` |
| Start new chapter | `python translator.py` |
| Monitor live progress | `python monitor_progress.py` |
| View recent logs | `python monitor_progress.py --tail` |

---

**Your Specific Case:**

Since you're currently at **section 26/31**, if the translation stops or you stop it:

```bash
python resume_translation.py
# Will resume from section 27
```

This saves you ~26 minutes of re-translation! 🎉

