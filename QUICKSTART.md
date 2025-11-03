# Quick Start Guide

Get started translating Pali texts in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Get API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

## Step 3: Set API Key

### Option A: Environment Variable (Recommended)

**Windows PowerShell:**
```powershell
$env:GOOGLE_API_KEY="paste-your-api-key-here"
```

**Windows Command Prompt:**
```cmd
set GOOGLE_API_KEY=paste-your-api-key-here
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY="paste-your-api-key-here"
```

### Option B: Enter When Prompted
The script will ask for your API key if not found in environment.

## Step 4: Run the Translator

```bash
python translator.py
```

## Step 5: Choose What to Translate

When prompted:
- Enter a chapter number (e.g., `1`) to translate one chapter
- Enter `all` to translate all chapters

## That's It!

The translator will:
1. ✅ Read the Pali text
2. ✅ Split it into manageable sections
3. ✅ Translate to English and Sinhala
4. ✅ Save structured JSON files

## Example Output

Your translated files will be saved in:
```
Pāthikavaggapāḷi/chapters/dn1-Pāthikasuttaṃ.json
```

Each file contains:
- Original Pali text
- English translation
- Sinhala translation
- Organized by sections

## What's Happening Behind the Scenes?

The translator automatically:
- 🔄 Handles rate limits (2-second delays)
- 📏 Manages character limits (4000 chars per chunk)
- 🧹 Cleans translation output
- 📝 Logs progress
- ⚠️ Handles errors gracefully

## Troubleshooting

### "No API key provided"
**Solution:** Set the `GOOGLE_API_KEY` environment variable

### "Rate limit exceeded"  
**Solution:** Increase `RATE_LIMIT_DELAY` in `config.py`

### "File not found"
**Solution:** Make sure you're in the correct directory with the Pali text files

## Next Steps

- 📖 Read [README.md](README.md) for detailed documentation
- ⚙️ Customize settings in [config.py](config.py)
- 🔍 Try [example_usage.py](example_usage.py) for code examples

## Tips for Best Results

1. **Start Small**: Try translating one chapter first
2. **Check Output**: Review the first translation to ensure quality
3. **Adjust Settings**: Modify `config.py` if needed
4. **Be Patient**: Translation takes time due to rate limiting (good thing!)
5. **Monitor Logs**: Check `translator.log` for detailed progress

## Need Help?

- Check the [README.md](README.md) for comprehensive documentation
- Review error messages in the console
- Check `translator.log` for detailed error information

---

**Happy Translating! 🙏**

May these translations help spread the Dhamma to more people around the world.

