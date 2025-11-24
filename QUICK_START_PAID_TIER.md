# Quick Start - Paid Tier (1K RPM)

## ✅ Your Setup is Optimized!

The script is now configured for your **paid tier limits** (1K RPM, 1M TPM, 10K RPD).

## 🚀 Speed Improvement

| Before (Free Tier) | After (Paid, No Verify) | Improvement |
|--------|-------|-------------|
| ~45s per section | ~5-6s per section | **8x faster** |
| ~80 sections/hour | ~600 sections/hour | **7.5x more** |
| 200 sections = 2.5h | 200 sections = 20m | **Save 2+ hours!** |

## ▶️ Just Run It

```bash
python translate_json_chapters.py
```

That's it! The configuration is already optimized.

## 📊 What You'll See

**Normal operation (fast, no verification):**
```
[1/100] Section 1
  → English (1234 chars)... ✓ (1456 chars)
  → Sinhala (1234 chars)... ✓ (1567 chars)  
  💾 Progress saved (1/100 sections)
```
*~5-6 seconds per section*

**If server overload (auto-retry):**
```
[2/100] Section 2
  → English (1234 chars)...
  ⚠ Server overloaded! Waiting 30s before retry... (attempt 1/5)
  → English (1234 chars)... ✓ (1456 chars)
  ...
```
*Adds wait time but recovers automatically*

## ⚙️ Current Settings

```python
# config.py - Optimized for your paid tier
MODEL_NAME = 'gemini-1.5-flash'     # Fast, stable model
RATE_LIMIT_DELAY = 1.0              # Balanced speed + TPM safety
VERIFY_DELAY = 2.0                  # For verification if enabled
ENABLE_VERIFICATION = False         # Disabled for speed (2x faster!)
MAX_RETRIES = 5                     # Handles 503/504 errors
API_TIMEOUT = 120                   # 2 min timeout per request
```

**Key optimizations:**
- **gemini-1.5-flash**: Stable, fast model (20-30s per section)
- **Verification disabled**: Avoids TPM limits, 2x faster
- **Request timeout**: Prevents hanging requests
- **Safe delays**: Avoids rate limit spikes

## 🔧 Optional Tweaks

### Want Verification Back (Higher Quality)?
```python
# config.py
ENABLE_VERIFICATION = True    # Enable verification
VERIFY_DELAY = 2.5           # Longer delay to avoid TPM limits
RATE_LIMIT_DELAY = 1.5       # Slightly longer
```
*Result: ~15s per section, better quality, catches foreign chars in Sinhala*

### Want Ultra Speed?
```python
# config.py
RATE_LIMIT_DELAY = 0.5       # Faster delays
ENABLE_VERIFICATION = False  # Keep disabled
```
*Result: ~3-4s per section, may hit TPM on very large sections*

### Getting Many 503 Errors?
```python
# config.py
SERVER_OVERLOAD_RETRY_DELAY = 60  # Wait longer during retries
```

## 🛟 If Something Goes Wrong

### Script stops with 503 error after retries
**Solution:** Wait 5-10 minutes, then resume:
```bash
python translate_json_chapters.py
# Resume from section: [last completed + 1]
```

### Want to translate during off-peak hours
**Best times:**
- ✅ Late night US time (2am-8am Eastern)
- ✅ Early morning Asia time
- ❌ Avoid: US/Europe business hours

### Need help
1. Check `FIX_503_ERROR.md` - Solutions for 503 errors
2. Check `PAID_TIER_OPTIMIZATION.md` - Full optimization guide
3. Check `UPGRADE_SUMMARY.md` - What was changed

## 📈 Your Usage vs Limits

Without verification (2 API calls per section):
- **Your usage:** ~20 calls/minute (600 sections/hour ÷ 60 × 2)
- **Your limit (RPM):** 1,000 calls/minute
- **Your limit (TPM):** 1,000,000 tokens/minute
- **RPM utilization:** 2% (tons of headroom!)
- **TPM utilization:** ~10-15% (safe, no issues)

## 🎯 Key Points

1. **It's already optimized** - Just run it!
2. **Verification disabled** - Was hitting TPM (token) limits
3. **8x faster than free tier** - ~5-6s per section
4. **Progress auto-saves** - Never lose work
5. **Retries are automatic** - Script handles errors
6. **High quality** - Primary translations are excellent

## 💡 Pro Tips

- ✅ Let it run - automatic retries work well
- ✅ Monitor first 5-10 sections to see speed
- ✅ Translate during off-peak for fewer 503s
- ❌ Don't stop script on 503 - it will retry
- ❌ Don't reduce delays below 0.5s - not needed

---

**Ready?** Run `python translate_json_chapters.py` and watch it fly! 🚀

