# Rate Limit Management Guide

## Understanding Google AI API Rate Limits

Google Generative AI has rate limits that vary by tier:

### Free Tier Limits
- **RPM (Requests Per Minute)**: 15 requests/minute
- **RPD (Requests Per Day)**: 1,500 requests/day
- **TPM (Tokens Per Minute)**: 1 million tokens/minute

### How Translation Uses API Calls

Each section translation makes **multiple API calls**:

1. **Without Verification** (2 calls per section):
   - English translation (1 call)
   - Sinhala translation (1 call)

2. **With Verification Enabled** (4-6 calls per section):
   - English translation (1 call)
   - English verification (1 call)
   - Sinhala translation (1 call)
   - Sinhala verification (1 call)
   - Sinhala character fix (1-2 calls if foreign characters detected)

### Rate Limit Math

**Example**: Translating 100 sections with verification enabled
- 100 sections × 5 calls avg = **500 API calls**
- At 15 RPM limit: **33+ minutes minimum**
- At 1,500 RPD limit: Would use **33% of daily quota**

## Current Configuration

The `config.py` file has been optimized to avoid rate limits:

```python
RATE_LIMIT_DELAY = 4        # 4 seconds between API calls
VERIFY_DELAY = 4            # 4 seconds for verification calls
ENABLE_VERIFICATION = True  # Enable two-phase translation
```

### Calculation
- With 4-second delays and verification:
  - Each section takes: ~20-30 seconds
  - Hourly capacity: ~120-180 sections
  - Daily capacity (8 hours): ~960-1,440 sections

## Strategies to Avoid Rate Limits

### 1. Increase Delays (Recommended)

Edit `config.py`:

```python
RATE_LIMIT_DELAY = 6        # Increase from 4 to 6 seconds
VERIFY_DELAY = 6            # Increase verification delay too
```

This gives you more buffer: **10 requests/minute** instead of 15.

### 2. Disable Verification (Faster but Lower Quality)

Edit `config.py`:

```python
ENABLE_VERIFICATION = False  # Disable verification phase
```

This **halves** API usage:
- 2 calls per section instead of 4-6
- Translations complete 2x faster
- But: No foreign character fixes, no readability improvements

### 3. Translate in Batches

Instead of translating entire books:
1. Translate 50-100 sections
2. Wait for rate limits to reset (1 hour)
3. Resume from where you stopped

The script supports resuming:
```bash
python translate_json_chapters.py
# When asked: "Resume from section number: 51"
```

### 4. Use Paid Tier (Best Solution)

Google AI paid tier offers:
- **60 RPM** (4x free tier)
- **10,000+ RPD** 
- Much faster translation

Cost is very reasonable (~$0.075 per 1M tokens for Gemini Flash).

## Handling Rate Limit Errors

The script now has **automatic retry with exponential backoff**:

1. Detects rate limit errors (429, "rate limit", "quota exceeded")
2. Waits progressively longer: 12s → 24s → 48s
3. Retries up to 3 times
4. If still failing, stops and tells you to wait

### What to Do When You Hit Limits

```
⚠ Rate limit exceeded! Waiting 12s before retry...
```

**Actions**:
1. **Let it retry** - The script will wait and retry automatically
2. **Stop and wait** - If it keeps failing, stop script (Ctrl+C) and wait 10-15 minutes
3. **Increase delays** - Edit `config.py` to use longer delays
4. **Check quota** - View your usage at https://aistudio.google.com/

## Optimizing for Different Scenarios

### Fast Translation (Risk Rate Limits)
```python
RATE_LIMIT_DELAY = 2
VERIFY_DELAY = 2
ENABLE_VERIFICATION = False
```
**Speed**: ~5-8 seconds/section  
**Risk**: High (may hit limits)

### Balanced (Recommended)
```python
RATE_LIMIT_DELAY = 4
VERIFY_DELAY = 4
ENABLE_VERIFICATION = True
```
**Speed**: ~20-30 seconds/section  
**Risk**: Low (safe for free tier)

### Safe Mode (Never Hit Limits)
```python
RATE_LIMIT_DELAY = 8
VERIFY_DELAY = 8
ENABLE_VERIFICATION = True
```
**Speed**: ~40-50 seconds/section  
**Risk**: Minimal (very safe)

## Monitoring Rate Limits

Watch for these messages:
- `⚠ Rate limit exceeded!` - Currently hitting limits
- `⚠ Response blocked` - Content safety issue
- `✓ Translation completed` - Success

Check logs in `translator.log` for detailed information.

## Foreign Character Issues

### Problem
Sometimes Sinhala translations contain Tamil/Hindi/Telugu characters instead of proper Sinhala.

Example from your file:
```
"දේවානම්inda"  ← "inda" is Latin, should be Sinhala
"දේවೇಂದ್ರය"     ← Contains Kannada character "ೇ" (U+0CC7)
```

### Solutions

1. **Automatic Fix During Translation** (Built-in)
   - Verification phase detects foreign characters
   - AI automatically fixes them
   - May add 1-2 extra API calls if issues found

2. **Fix Existing Files** (Use utility script)
   ```bash
   python fix_invalid_characters.py
   ```
   - Scans JSON files for invalid characters
   - Shows all issues
   - Uses AI to fix them
   - Creates backups before modifying

### Using the Fix Script

```bash
python fix_invalid_characters.py
```

**Scan only** (find issues):
```
Enter path: Mahāvaggapāḷi/chapters/dn21-Sakkapañhasuttaṃ.json
Run mode: (s)can only
```

**Fix issues**:
```
Enter path: Mahāvaggapāḷi/chapters/
Run mode: (f)ix issues
```

**Dry run** (see what would be fixed):
```
Enter path: Mahāvaggapāḷi/chapters/
Run mode: (d)ry-run fix
```

## Best Practices

1. **Start Small**: Test on 1-2 sections first
2. **Monitor Logs**: Check `translator.log` for issues
3. **Use Backups**: Script creates `.backup` files automatically
4. **Resume Feature**: Always use resume if interrupted
5. **Off-Peak Hours**: Translate during less busy times
6. **Batch Work**: Do 100-200 sections, then take a break

## Troubleshooting

### "Rate limit exceeded after 3 retries"
→ Wait 30-60 minutes, then resume translation

### "Foreign characters detected in Sinhala"
→ Run `fix_invalid_characters.py` on the file

### "Translation suspiciously long"
→ Normal warning, check if output makes sense

### Script keeps failing at same section
→ That section may have problematic content, skip it manually

## Summary

- **Free tier**: Be conservative with delays (4+ seconds)
- **Enable verification**: Better quality but slower
- **Use resume**: Don't start over if interrupted
- **Fix characters**: Run fix script after translation
- **Upgrade tier**: If translating large volumes regularly

