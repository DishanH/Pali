# 📊 Translation Progress Monitoring Guide

## Your Current Status

✅ **GOOD NEWS: Translator IS Working!**

Based on the status check:
- 🟢 Status: RUNNING (active 2 minutes ago)
- 📝 Progress: Section 26/31 (83% complete)
- ⏱️ Est. remaining: ~5 minutes
- 📁 Output: 2 chapters completed (dn1, dn2)

## Why It Seems Slow

After changing the model in `config.py` to `gemini-2.5-flash`, the API response times may have changed:
- Different models have different processing speeds
- Some models take longer but produce better quality
- Rate limiting still applies (2-second delays)
- Network latency can vary

## How to Monitor Progress

### Method 1: Quick Status Check (Recommended)

```bash
python check_status.py
```

**Shows:**
- ✅ Current status (Active/Working/Stuck)
- 📝 Section progress with progress bar
- ⏱️ Estimated time remaining
- 📁 Completed output files
- ❌ Any errors

**Run this anytime** to see instant status without interrupting the translator.

### Method 2: Live Monitoring

```bash
python monitor_progress.py
```

**Features:**
- 📊 Real-time updates every 5 seconds
- 🕐 Shows seconds since last activity
- ⚠️ Warns if stuck (>5 minutes idle)
- 📈 Progress bar and estimates

**Press Ctrl+C to exit** (won't stop the translator)

### Method 3: Check Log File Directly

```bash
# Show last 20 lines
python monitor_progress.py --tail

# Show last 50 lines
python monitor_progress.py --tail --lines 50

# Watch log in real-time (Windows PowerShell)
Get-Content translator.log -Wait -Tail 20
```

## Understanding the Output

### Console Output (with new improvements)

Now you'll see real-time progress in the console:

```
[1/48] Translating section 1...
  → English translation (1234 chars)... ✓ (2100 chars)
  → Sinhala translation (1234 chars)... ✓ (1800 chars)

[2/48] Translating section 2...
  → English translation (567 chars)... ✓ (890 chars)
  → Sinhala translation (567 chars)... ✓ (750 chars)
```

### Log File

The `translator.log` shows detailed activity:
- Timestamps for every action
- Section numbers and character counts
- Translation completion confirmations
- Any errors or warnings

## What If It's Stuck?

### Signs It's Working ✅
- ✓ Status shows "ACTIVE" or "WORKING"
- ✓ Last activity < 2 minutes ago
- ✓ Section numbers increasing
- ✓ Output files being updated

### Signs It Might Be Stuck ⚠️
- ⚠️ Status shows ">5 minutes idle"
- ⚠️ No log updates for >5 minutes
- ⚠️ Errors in recent log entries
- ⚠️ Section number not changing

### If Stuck, Check:

1. **API Issues?**
   ```bash
   # Check last few log lines for errors
   python monitor_progress.py --tail --lines 30
   ```

2. **Rate Limit Hit?**
   - Look for "Rate limit exceeded" or "429" errors
   - Solution: Increase `RATE_LIMIT_DELAY` in `config.py`

3. **Model Issues?**
   - The new model name might be wrong
   - Check valid model names:
     - `gemini-1.5-flash` (fast, cheaper)
     - `gemini-1.5-pro` (slower, better quality)
     - `gemini-2.0-flash-exp` (experimental)

4. **Network Issues?**
   - Check internet connection
   - API might be temporarily down

## Translation Time Estimates

### Per Section (approximate)
- English translation: 10-30 seconds
- Sinhala translation: 10-30 seconds
- Rate limiting delays: 2 seconds × 2 = 4 seconds
- **Total per section: ~30-60 seconds**

### Per Chapter
- **48 sections** (like dn1): ~40-60 minutes
- **31 sections** (like dn3): ~25-40 minutes
- **Varies** by section length and model speed

### Why Longer with New Model?
- Different models have different processing times
- `gemini-2.5-flash` might be:
  - More thorough (better quality)
  - Newer (potentially slower API)
  - Different infrastructure

## Improving Speed

### Option 1: Use Faster Model
Edit `config.py`:
```python
MODEL_NAME = 'gemini-1.5-flash'  # Faster, still good quality
```

### Option 2: Reduce Rate Limiting (Risky)
Edit `config.py`:
```python
RATE_LIMIT_DELAY = 1  # From 2 to 1 second
# WARNING: May hit rate limits!
```

### Option 3: Increase Chunk Size (if sections are small)
Edit `config.py`:
```python
MAX_CHUNK_SIZE = 6000  # From 4000 (combine more sections)
```

## Best Practices

### While Translation is Running

✅ **DO:**
- Run `python check_status.py` periodically to monitor
- Let it run in background
- Check `translator.log` if concerned
- Be patient (translation takes time!)

❌ **DON'T:**
- Close the terminal running the translator
- Interrupt with Ctrl+C (unless you want to stop)
- Run multiple translators simultaneously
- Change config while running

### After Completion

✅ Check output files:
```bash
ls Pāthikavaggapāḷi\chapters\
```

✅ Verify JSON structure:
```bash
python -m json.tool Pāthikavaggapāḷi\chapters\dn1-Pāthikasuttaṃ.json
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python check_status.py` | Quick status snapshot |
| `python monitor_progress.py` | Live monitoring |
| `python monitor_progress.py --tail` | Show recent logs |
| Check `translator.log` | Detailed activity log |
| Check `Pāthikavaggapāḷi\chapters\` | Output files |

## Troubleshooting Commands

```bash
# See if translator is still running
python check_status.py

# Watch live progress
python monitor_progress.py

# Check for errors
python monitor_progress.py --tail --lines 50 | Select-String "ERROR"

# View last completed section
python monitor_progress.py --tail

# Check output files
Get-ChildItem Pāthikavaggapāḷi\chapters\*.json | Select-Object Name, Length, LastWriteTime
```

## FAQ

**Q: How do I know it's still working?**  
A: Run `python check_status.py` - if last activity is < 2 minutes ago, it's working.

**Q: Can I check progress without interrupting?**  
A: Yes! Both monitoring scripts just read the log file, they don't interfere.

**Q: What if I need to stop it?**  
A: Press Ctrl+C in the translator terminal. Completed chapters are already saved.

**Q: How do I resume if stopped?**  
A: Just run `python translator.py` again and select the next chapter.

**Q: Why 20+ minutes for one chapter?**  
A: Normal! 48 sections × ~30 seconds = 24+ minutes, plus API variability.

**Q: Can I speed it up?**  
A: Use a faster model or reduce rate delay, but be careful of API limits.

---

## Your Immediate Next Steps

1. **Check current status:**
   ```bash
   python check_status.py
   ```

2. **If it's working (< 5 min idle):**
   - ✅ Just wait, it's progressing
   - ✅ Run status checks periodically
   - ✅ Be patient!

3. **If it seems stuck (> 5 min idle):**
   - Check for errors: `python monitor_progress.py --tail`
   - Consider restarting with faster model
   - Check API key and network

4. **Monitor live (optional):**
   ```bash
   python monitor_progress.py
   ```

---

**Remember:** Translation is slow by design (rate limiting protects your API quota). Progress monitoring tools help you know it's working! 🙏

