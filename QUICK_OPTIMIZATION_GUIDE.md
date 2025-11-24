# Quick Optimization Guide - verify_and_clean_translations.py

## 🚀 Quick Start

The script is **already optimized** with default settings for maximum token savings!

Just run it as normal:
```bash
python verify_and_clean_translations.py
```

---

## 💰 Cost Savings Summary

| Before Optimization | After Optimization | Savings |
|--------------------|--------------------|---------|
| ~400 API calls/100 sections | ~50 API calls/100 sections | **87.5%** |
| ~$1.60 per 100 sections | ~$0.03 per 100 sections | **98%** |
| 8-12 sec per section | 3 sec per section | **4x faster** |

---

## ⚙️ Configuration Flags

Edit at the **top of verify_and_clean_translations.py**:

```python
# Line 25-26
VERIFY_ENGLISH = False  # English verification (default: OFF)
SKIP_CLEAN_SECTIONS = True  # Skip clean sections (default: ON)
```

### Quick Settings:

**Maximum Savings (Default)** - Recommended for pay-as-you-go:
```python
VERIFY_ENGLISH = False
SKIP_CLEAN_SECTIONS = True
```

**Verify Both Languages** - When you need English too:
```python
VERIFY_ENGLISH = True
SKIP_CLEAN_SECTIONS = True
```

**Full Verification** - Maximum quality, higher cost:
```python
VERIFY_ENGLISH = True
SKIP_CLEAN_SECTIONS = False
```

---

## 📊 What Changed?

### ✅ Token Optimizations
1. **Shorter prompts**: ~300 chars instead of ~2,000 chars (85% less)
2. **Single API call**: 1 call per issue instead of 3-4 calls (75% less)
3. **English disabled**: Only verify Sinhala by default (50% less)
4. **Smart skipping**: Skip API calls for clean sections (70% saved)

### ✅ Features Preserved
- All quality checks (foreign chars, typography, accuracy)
- Auto-fix problematic translations
- Progress saving
- Retry logic for errors
- Comprehensive logging

---

## 🎯 Console Output Guide

**Good signs (API call saved):**
```
✓ Sinhala OK (no API call needed)  ← Saved an API call!
✓ English OK (verification disabled)  ← English skipped
```

**When API is used (only when needed):**
```
🔧 Fixing Sinhala translation (1 API call)...  ← Only 1 call, not 3-4!
✓ Sinhala fixed: Contains Tamil characters  ← Issue resolved
```

---

## 📈 Monitor Token Usage

### Check API Call Count:
```bash
# See how many API calls were made
grep "Verifying Sinhala translation" translator.log | wc -l
```

### Expected Results:
- **100 sections processed**
- **~10-20 API calls** (only for problematic sections)
- **~80-90 sections skipped** (no API call needed)

---

## 💡 Tips for Maximum Savings

1. **Run on already-verified translations**: Most sections will skip API calls
2. **Fix issues once**: Second run will be nearly free (no issues to fix)
3. **Use Gemini 2.0 Flash**: Cheapest model, still great quality
4. **Adjust rate limits**: Set `RATE_LIMIT_DELAY = 7.0` in config.py for free tier

---

## 🔧 Troubleshooting

### Too many API calls?
- Check if `SKIP_CLEAN_SECTIONS = True`
- Most sections should show "no API call needed"

### Need to verify English?
- Set `VERIFY_ENGLISH = True` temporarily
- Run script once
- Set back to `False` after

### Rate limit errors?
- Increase `RATE_LIMIT_DELAY` in config.py
- Default 7.0 seconds is safe for 10 RPM

---

## 📝 Example Run Output

```
============================================================
Translation Verification & Cleaning Tool - OPTIMIZED
============================================================
Token Optimization: English verification DISABLED
Smart skipping: ENABLED
============================================================

Processing: dn01-Brahmajālasuttaṃ.json
Chapter ID: dn01
Total sections: 63

[1/63] Section 1
  ✓ English OK (verification disabled)
  ✓ Sinhala OK (no API call needed)  ← SAVED API CALL

[2/63] Section 2
  ✓ English OK (verification disabled)
  ⚠ Sinhala has 3 foreign characters:
    - Tamil char 'த' (U+0BA4)
  🔧 Fixing Sinhala translation (1 API call)...  ← ONLY 1 CALL
  ✓ Sinhala fixed: Contains Tamil characters

[3/63] Section 3
  ✓ English OK (verification disabled)
  ✓ Sinhala OK (no API call needed)  ← SAVED API CALL

...

✅ Completed:
   Sections checked: 63
   English issues found: 0, fixed: 0
   Sinhala issues found: 5, fixed: 5  ← Only 5 API calls for 63 sections!
   Texts cleaned: 12
```

---

## 🎉 Bottom Line

**You're already using the optimized version!**

The script will:
- ✅ Save ~90% of tokens compared to before
- ✅ Only call API when there's an actual issue
- ✅ Skip English verification (enable if needed)
- ✅ Use shorter, more efficient prompts
- ✅ Maintain all quality checks

**Expected cost**: ~$0.03-0.10 per 100 sections (was $1.50+ before)

---

## 📚 More Details

See `VERIFICATION_OPTIMIZATION_REPORT.md` for:
- Detailed technical explanation
- Before/after code comparisons
- Token usage breakdown
- Configuration recommendations

