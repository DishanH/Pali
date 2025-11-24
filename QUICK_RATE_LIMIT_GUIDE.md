# Quick Rate Limit Guide 🚀

## The Fix (TL;DR)

**Problem**: Getting `RPM 10/10` errors  
**Solution**: Increased delay from 3s to 7s + added smart rate limiter  
**Result**: Translations work reliably (but slower)

---

## Quick Start

1. **Just run your script**:
   ```bash
   python translate_json_chapters.py
   ```

2. **When asked for RPM limit**, press **Enter** (uses 10 RPM default)

3. **That's it!** The script now handles rate limiting automatically.

---

## What Changed

| Before | After |
|--------|-------|
| 3 seconds between calls | 7 seconds between calls |
| No rate limit tracking | Intelligent rate limiter |
| Frequent 429 errors | Automatic waiting + no errors |
| ~20 requests/min (too fast!) | Max 8-9 requests/min (safe) |

---

## Your API Limits

### Free Tier (Most Common):
- **RPM**: 10 requests per minute
- **Required delay**: 7+ seconds
- **Speed**: ~12-15 min per 50 sections

### Pay-As-You-Go:
- **RPM**: 10 requests per minute (same as free!)
- **Required delay**: 7+ seconds  
- **Speed**: ~12-15 min per 50 sections

### Higher Tiers:
- **RPM**: 15-1000 requests per minute
- **Enter your RPM** when script asks
- **Speed**: Much faster!

---

## What You'll See

### Normal Operation:
```
[1/50] Section 1
  → English (4532 chars)... ✓ (1245 chars)
  → Sinhala (4532 chars)... ✓ (1823 chars)
  💾 Progress saved (1/50 sections)
```

### When Rate Limiter Activates:
```
[6/50] Section 6
  → English (8234 chars)... ✓ (2456 chars)
  ⏱️  Rate limit protection: waiting 12.3s (made 10 calls in last 48s)
  → Sinhala (8234 chars)... ✓ (3124 chars)
```

**This is NORMAL and GOOD** - it prevents errors!

---

## Still Getting Errors?

### Option 1: Increase Delay (Easiest)
Edit `config.py`:
```python
RATE_LIMIT_DELAY = 9.0  # or 10.0 for extra safety
```

### Option 2: Enter Correct RPM When Asked
When script asks:
```
Enter your API RPM limit (10 for free tier, 15 for basic, press Enter for default 10):
```

Enter your actual limit (check at https://aistudio.google.com/app/apikey)

### Option 3: Wait & Retry
If you just hit the limit:
1. Wait 60 seconds
2. Run script again
3. Use `resume_from=X` to continue where you left off

---

## Expected Speed (10 RPM)

| Sections | Time Estimate |
|----------|---------------|
| 10 sections | 2-3 minutes |
| 50 sections | 12-15 minutes |
| 100 sections | 25-30 minutes |
| 200 sections | 50-60 minutes |

**Why so slow?**  
- Free tier = 10 requests per minute maximum
- Each section = 2 requests (English + Sinhala)
- 7 seconds × 2 = 14 seconds per section minimum
- Rate limiter may add extra waiting time

This is **normal and expected** with free tier! 🎯

---

## Pro Tips

### 1. Run Overnight for Large Books
- 500+ sections? Start before bed
- Script saves progress after each section
- Can resume if interrupted

### 2. Check Progress
```bash
tail -f translator.log
```

### 3. Resume from Specific Section
If script stops:
```bash
# It will tell you: "Resume with: resume_from=45"
# Next time, enter 45 when asked for resume section
```

### 4. Disable Verification (Faster)
Already disabled in `config.py`:
```python
ENABLE_VERIFICATION = False
```
This cuts API calls in half!

---

## Configuration Reference

### Key Settings in `config.py`:

```python
# Main rate limit control (MOST IMPORTANT)
RATE_LIMIT_DELAY = 7.0  # Seconds between API calls

# Verification (disabled to save API calls)
ENABLE_VERIFICATION = False

# Retry settings
MAX_RETRIES = 5
RETRY_DELAY = 5
SERVER_OVERLOAD_RETRY_DELAY = 30
```

---

## Check Your API Quota

1. Go to: https://aistudio.google.com/app/apikey
2. Click on your API key
3. Check "Quota" section
4. Look for "GenerateRequestsPerMinutePerProjectPerModel"

---

## Summary

✅ Rate limiting now automatic  
✅ No more 429 errors  
✅ Progress saved after each section  
✅ Can resume if interrupted  
✅ Visual feedback when waiting  

**Just run it and let it work!** ☕

The slower speed is necessary to stay within API limits - there's no way around it with the free tier.

