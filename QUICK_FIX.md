# Quick Fix Guide for Rate Limits & Character Issues

## 🚨 Emergency: Hit Rate Limit

```bash
# Stop the script (Ctrl+C)
# Wait 10-15 minutes
# Then resume from where you stopped

python translate_json_chapters.py
# When asked: Resume from section number: [enter section number]
```

## ⚡ Prevent Rate Limits

Edit `config.py`:

```python
# Slower but safer - won't hit limits
RATE_LIMIT_DELAY = 6        # Increase from 4 to 6
VERIFY_DELAY = 6            # Increase from 4 to 6

# OR disable verification (faster, uses half the API calls)
ENABLE_VERIFICATION = False
```

## 🔧 Fix Invalid Characters in Existing Files

Your file has characters like: `දේවානම්inda` (should be all Sinhala)

```bash
# Run the character fix utility
python fix_invalid_characters.py

# Enter path to your file or directory
Path: Mahāvaggapāḷi/chapters/dn21-Sakkapañhasuttaṃ.json

# Choose fix mode
Mode: f (for fix)
```

The script will:
1. Find all foreign characters (Tamil, Hindi, Telugu, Kannada, etc.)
2. Use AI to replace them with proper Sinhala
3. Create a backup (`.backup` file)
4. Save the corrected version

## 📊 Rate Limit Math (Free Tier)

| Setting | API Calls/Section | Sections/Hour | Hit Limit Risk |
|---------|------------------|---------------|----------------|
| No verification | 2 calls | ~450 sections | Medium |
| With verification (delay=2s) | 4-6 calls | ~180 sections | **HIGH** |
| With verification (delay=4s) | 4-6 calls | ~120 sections | Low |
| With verification (delay=6s) | 4-6 calls | ~90 sections | **Very Low** |

**Free tier limits**: 15 requests/minute, 1,500 requests/day

## ✅ Recommended Settings

For translating Buddhist texts with best quality:

```python
# config.py
RATE_LIMIT_DELAY = 4        # Safe for free tier
VERIFY_DELAY = 4            # Ensures character validation
ENABLE_VERIFICATION = True  # Fixes foreign characters automatically
```

## 🎯 Your Specific Issues

### Issue 1: Rate Limits
**Symptom**: Script says "Rate limit exceeded"  
**Fix**: Increase `RATE_LIMIT_DELAY` to 6 in `config.py`

### Issue 2: Invalid Characters (දේවานම්inda, දේවೇಂದ್ರය)
**Symptom**: Mixed Latin/Kannada/Tamil characters in Sinhala  
**Fix**: Run `python fix_invalid_characters.py`

### Issue 3: Verification Not Working
**Symptom**: Foreign characters not being caught  
**Root cause**: Rate limits prevent verification from running  
**Fix**: 
1. Increase delays to avoid rate limits
2. Let verification run properly
3. Or use fix_invalid_characters.py after translation

## 🔄 Resume Workflow

If you have to stop:
1. Note the last completed section number
2. Resume from next section:
   ```bash
   python translate_json_chapters.py
   # Resume from section number: [last completed + 1]
   ```

## 📝 Check Your File

View sections with issues:
```bash
# On Windows PowerShell
Get-Content "Mahāvaggapāḷi\chapters\dn21-Sakkapañhasuttaṃ.json" | Select-String "inda|ೇ"

# On Linux/Mac
grep -n "inda\|ೇ" "Mahāvaggapāḷi/chapters/dn21-Sakkapañhasuttaṃ.json"
```

## 💡 Pro Tips

1. **Translate during off-peak hours** (night/early morning) - less rate limiting
2. **Save often** - Script auto-saves after each section
3. **Batch processing** - Do 50-100 sections, take a break, continue
4. **Check logs** - `translator.log` has detailed information
5. **Backup first** - Copy files before fixing characters

## 📞 Need More Help?

See detailed guide: `RATE_LIMIT_GUIDE.md`

