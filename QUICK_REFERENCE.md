# Quick Reference - Translation Resume

## 🚀 Quick Start

### Resume Your Translation
```bash
python resume_translation.py
```

### Start New Translation
```bash
python translator.py
```

## 📊 What's New

### ✅ Automatic Progress Saving
- Saves after **every section** translated
- No more lost work!
- Partial files marked with `_partial: true`

### 🔄 Smart Resume
- Automatically detects where you left off
- Shows progress: "17/34 sections completed"
- Continues from exact section

### 🛡️ Better Error Handling
- **Automatic retries**: 3 attempts with increasing delays
- **Handles API blocks**: Finish reason 8 (safety filters)
- **Rate limit aware**: Respects API quotas

## 🔍 Your Current Situation

Based on your error log, you were translating:
- **Chapter**: dn6 (Pāsādikasuttaṃ)
- **Section**: 18/34
- **Error**: finish_reason 8 (API blocked the response)

### What Happened?
The API blocked the Sinhala translation of section 18, likely due to:
- Safety filters
- Content policy detection
- Rate limiting

### What's Saved?
- Sections 1-17 are **fully translated** ✓
- Section 18 English is **complete** ✓
- Section 18 Sinhala **failed** ✗

## 🎯 How to Resume

### Option 1: Use Resume Script (Recommended)
```bash
python resume_translation.py
```

**However**: Since the error happened before the first save, there's no partial file yet.

### Option 2: Start Fresh on dn6
```bash
python translator.py
# Choose chapter 6 (dn6)
```

The new version will:
1. Save progress after section 1 ✓
2. Save progress after section 2 ✓
3. ... and so on
4. If it fails at section 18 again, you'll have sections 1-17 saved
5. You can resume from section 18

## ⚙️ Recommended Settings

For better reliability with dn6:

Edit `config.py`:
```python
# Increase delay between API calls
RATE_LIMIT_DELAY = 3  # Was 2, now 3 seconds

# Disable verification temporarily (reduces API calls)
ENABLE_VERIFICATION = False  # Was True

# Or use a different model
MODEL_NAME = 'gemini-1.5-flash'  # Alternative model
```

## 🔧 Troubleshooting

### Error: finish_reason 8
**Solution**: Wait 10-15 minutes, then retry
- API may be temporarily blocking content
- Retry logic will attempt 3 times automatically

### Error: 429 Resource exhausted
**Solution**: Increase delays
```python
RATE_LIMIT_DELAY = 5  # Increase to 5 seconds
```

### No partial file found
**Cause**: Error happened before first section completed
**Solution**: Start translation again - it will now save incrementally

## 📈 Progress Tracking

### Check What's Completed
```bash
ls -la Pāthikavaggapāḷi/chapters/
```

Look for:
- `dn1-Pāthikasuttaṃ.json` ✓ Complete
- `dn2-Udumbarikasuttaṃ.json` ✓ Complete
- `dn3-Cakkavattisuttaṃ.json` ✓ Complete
- `dn4-Aggaññasuttaṃ.json` ✓ Complete
- `dn5-Sampasādanīyasuttaṃ.json` ✓ Complete
- `dn6-Pāsādikasuttaṃ.json` ✗ Failed (no file)

### Check Partial Progress
```bash
python -c "import json; data=json.load(open('Pāthikavaggapāḷi/chapters/dn6-Pāsādikasuttaṃ.json')); print(f'{data.get(\"_completed_sections\", 0)}/{data.get(\"_total_sections\", 0)} sections')"
```

## 💡 Tips

1. **Monitor the console**: Watch for warnings and progress
2. **Check logs**: `translator.log` has detailed info
3. **Be patient**: Some sections take longer
4. **Retry later**: If blocked, wait 15 minutes
5. **Backup**: Copy completed chapters to a safe location

## 📞 Next Steps

### Immediate Action
```bash
# Wait 10-15 minutes for API cooldown
# Then run:
python translator.py
# Choose chapter 6 (dn6)
```

### If It Fails Again
1. Check `translator.log` for specific error
2. Try with `ENABLE_VERIFICATION = False`
3. Increase `RATE_LIMIT_DELAY = 5`
4. Consider different time of day (less API load)

## 📚 Full Documentation

See `RESUME_GUIDE.md` for complete details on:
- Error scenarios
- Configuration options
- Technical details
- Troubleshooting guide
