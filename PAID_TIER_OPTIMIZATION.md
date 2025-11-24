# Paid Tier Optimization Guide

## Overview

This guide is for users with **Google AI paid billing** who have higher rate limits:
- **RPM**: 1,000 requests per minute
- **TPM**: 1,000,000 tokens per minute  
- **RPD**: 10,000+ requests per day

The default configuration has been optimized for paid tier users to maximize speed while maintaining reliability.

## Current Optimized Settings

### config.py Settings (Optimized for Paid Tier)

```python
# Fast translation with paid tier limits
RATE_LIMIT_DELAY = 0.5              # 0.5s between calls (vs 5s for free tier)
VERIFY_DELAY = 0.5                  # 0.5s verification delay
ENABLE_VERIFICATION = True          # Quality verification enabled
MAX_RETRIES = 5                     # More retries for 503 errors
RETRY_DELAY = 5                     # Base retry delay
SERVER_OVERLOAD_RETRY_DELAY = 30    # Special delay for 503 errors
```

### Performance Comparison

| Tier | Delay | Sections/Hour | Time per Section | Daily Capacity |
|------|-------|---------------|------------------|----------------|
| **Free Tier** | 5s | ~80 | ~45s | ~640 |
| **Paid Tier (Optimized)** | 0.5s | ~400 | ~9s | ~3,200 |

### Speed Improvement

With paid tier optimization:
- **5-6x faster** than free tier settings
- ~9 seconds per section (with verification)
- ~400 sections per hour
- Can translate a 200-section chapter in ~30 minutes

## Understanding Error Types

### 503 Server Overload (Not Your Fault!)

```
ERROR: 503 The model is overloaded. Please try again later.
```

**What it means:**
- The Google AI server is experiencing high demand
- NOT a rate limit issue (you have capacity)
- Temporary server congestion

**How it's handled:**
- Automatic retry with longer delays: 30s → 60s → 90s → 120s → 150s
- Up to 5 retry attempts
- Linear backoff (not exponential) for server overload

### 429 Rate Limit (Your Quota)

```
ERROR: 429 Rate limit exceeded
```

**What it means:**
- You've exceeded your RPM/TPM limits
- Need to slow down requests

**How it's handled:**
- Exponential backoff: 10s → 20s → 40s → 80s
- Should rarely happen with paid tier

### Timeout Errors

```
ERROR: Timeout of 600.0s exceeded
```

**What it means:**
- Request took too long to process
- Large text chunks or slow server response

**How it's handled:**
- Automatic retry with linear backoff
- Up to 5 attempts

## Customizing for Your Needs

### Maximum Speed (Aggressive)

If you rarely see 503 errors and want maximum speed:

```python
# config.py
RATE_LIMIT_DELAY = 0.2              # Very fast
VERIFY_DELAY = 0.2
ENABLE_VERIFICATION = False         # Skip verification for speed
MAX_RETRIES = 3
```

**Result**: ~5-6 seconds per section, ~600 sections/hour

### Balanced (Recommended - Current Settings)

```python
# config.py
RATE_LIMIT_DELAY = 0.5              # Current default
VERIFY_DELAY = 0.5
ENABLE_VERIFICATION = True
MAX_RETRIES = 5
```

**Result**: ~9 seconds per section, ~400 sections/hour

### Conservative (If You Get Frequent 503s)

If you're seeing many 503 errors during peak hours:

```python
# config.py
RATE_LIMIT_DELAY = 1.0              # Slower
VERIFY_DELAY = 1.0
ENABLE_VERIFICATION = True
MAX_RETRIES = 5
SERVER_OVERLOAD_RETRY_DELAY = 45    # Longer waits
```

**Result**: ~15 seconds per section, ~240 sections/hour

## When You See Errors

### 503 Server Overload

**During translation:**
```
→ English (1234 chars)...
  ⚠ Server overloaded! Waiting 30s before retry... (attempt 1/5)
  ⚠ Server overloaded! Waiting 60s before retry... (attempt 2/5)
```

**What to do:**
1. ✅ **Let it retry** - The script handles this automatically
2. ✅ **Be patient** - Server overload is temporary (usually 1-2 minutes)
3. ❌ **Don't stop the script** - It will eventually succeed
4. ❌ **Don't reduce delays** - Won't help with server overload

**If it fails after 5 retries:**
- Wait 5-10 minutes
- Resume from the last saved section
- Try again during off-peak hours (avoid peak US/Europe hours)

### Rate Limit Errors (Rare)

If you somehow hit rate limits:
```
  ⚠ Rate limit exceeded! Waiting 10s before retry...
```

**Solutions:**
1. Increase `RATE_LIMIT_DELAY` to 1.0
2. Disable verification temporarily: `ENABLE_VERIFICATION = False`
3. Check your API quota at https://aistudio.google.com/

## Monitoring Your Usage

### During Translation

Watch for these patterns:

✅ **Healthy** (optimal speed):
```
[1/100] Section 1
  → English (1234 chars)... ✓ (1456 chars)
  → Verifying English... ✓
  → Sinhala (1234 chars)... ✓ (1567 chars)
  → Verifying Sinhala... ✓
  💾 Progress saved (1/100 sections)
```
*Time: ~8-10 seconds per section*

⚠️ **Occasional 503** (acceptable):
```
  → English (1234 chars)...
  ⚠ Server overloaded! Waiting 30s before retry... (attempt 1/5)
  → English (1234 chars)... ✓ (1456 chars)
```
*Happens during peak hours, automatic recovery*

❌ **Frequent 503s** (need adjustment):
```
  ⚠ Server overloaded! Waiting 30s... (attempt 1/5)
  ⚠ Server overloaded! Waiting 60s... (attempt 2/5)
  ⚠ Server overloaded! Waiting 90s... (attempt 3/5)
```
*If you see this on most sections, increase delays*

## API Call Math

### Per Section (With Verification)

```
1. English translation      → 1 API call + 0.5s delay
2. English verification     → 1 API call + 0.5s delay
3. Sinhala translation      → 1 API call + 0.5s delay
4. Sinhala verification     → 1 API call + 0.5s delay
5. (Optional) Sinhala fix   → 1-2 API calls if foreign chars detected

Total: 4-6 API calls, ~2-3 seconds in delays per section
```

### Rate Limit Usage

With optimal settings (0.5s delays):
- **Sections per minute**: ~6-7 sections
- **API calls per minute**: ~24-28 calls
- **RPM usage**: 2.4% of 1,000 RPM limit
- **Safe margin**: Very safe, room for 40x more speed!

## Troubleshooting

### Problem: "Timeout of 600.0s exceeded"

**Cause:** Request took over 10 minutes (shouldn't happen normally)

**Solutions:**
1. Check your internet connection
2. Try a different model: `MODEL_NAME = 'gemini-1.5-flash'`
3. Reduce chunk size if processing very large sections

### Problem: Frequent 503 errors during specific times

**Cause:** Google AI server congestion during peak hours

**Solutions:**
1. Translate during off-peak hours (late night US time)
2. Increase `SERVER_OVERLOAD_RETRY_DELAY = 60` for longer waits
3. Consider using `gemini-1.5-pro` (usually less congested but costs more)

### Problem: Progress is saved but some sections missing translations

**Cause:** Script stopped mid-translation due to errors

**Solution:**
```bash
python translate_json_chapters.py
# When asked: "Resume from section number: [last_section + 1]"
```

The script automatically saves after each section, so you never lose progress.

## Best Practices

1. **Monitor first few sections** - Watch for patterns in the first 5-10 sections
2. **Adjust based on errors** - If you see frequent 503s, increase delays slightly
3. **Use peak/off-peak wisely** - Translate during off-peak hours for best speed
4. **Keep verification enabled** - Quality is worth the extra 2-3 seconds per section
5. **Don't panic on 503s** - They're temporary and handled automatically

## Summary

| Aspect | Free Tier | Paid Tier (Optimized) |
|--------|-----------|----------------------|
| Delay | 5s | 0.5s |
| Speed | ~45s/section | ~9s/section |
| Capacity | ~80 sections/hour | ~400 sections/hour |
| 503 Handling | 3 retries, short waits | 5 retries, longer waits |
| Rate Limit Risk | High | Very Low |

**Bottom line:** Paid tier is configured for **5-6x faster translation** with robust error handling for 503 server overload issues.

