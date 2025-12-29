# Bulk Translation Guide - Fast Track

This is the **fast track** approach to translate all 1,603 missing Pali terms in one go using external tools like Perplexity, ChatGPT, or Google Translate.

## 🚀 Quick Overview

Instead of waiting 5 months with daily quotas, you can:
1. **Extract all missing terms** → Done! ✅
2. **Use external tool to translate all at once** → Your task
3. **Apply all translations back** → One command

## 📁 Files Generated

After running `python create_bulk_translation_json.py`, you get:

### 1. `bulk_translations_simple.json` (Recommended)
```json
[
  {
    "pali": "Dutiyavaggo",
    "english": "",
    "sinhala": "",
    "usage_count": 11,
    "sample_context": "Vagga Title: sn.5.8/Section 909"
  }
]
```
**Perfect for**: Copy-paste into ChatGPT, Claude, or Perplexity

### 2. `bulk_translations.txt` (Alternative)
```
Dutiyavaggo | 11 uses | Vagga Title: sn.5.8/Section 909
Bhikkhusuttaṃ | 10 uses | Section Title: sn.5.2/Section 186
```
**Perfect for**: Simple copy-paste, spreadsheet import

### 3. `bulk_translations.json` (Complete)
Full version with all metadata and contexts - this is what gets updated with your translations.

## 🎯 Translation Workflow

### Step 1: Choose Your Tool
- **Perplexity Pro** (Recommended)
- **ChatGPT Plus** 
- **Claude Pro**
- **Google Translate** (bulk upload)
- **DeepL Pro**

### Step 2: Prepare Your Prompt

**For Perplexity/ChatGPT/Claude:**
```
I need to translate 1603 Pali Buddhist terms to English and Sinhala. 

Here's the JSON format with the terms:
[Copy the content of bulk_translations_simple.json]

Please fill in the "english" and "sinhala" fields for each term. 
Context: These are Buddhist canonical terms from Pali texts.
- Keep translations consistent with Buddhist terminology
- Use the "sample_context" to understand usage
- Terms ending in "suttaṃ" are discourse titles
- Terms ending in "vaggo" are chapter/section names

Return the completed JSON with all translations filled in.
```

### Step 3: Process in Chunks (if needed)

If 1603 terms is too much for one request, split the JSON:

```bash
# Split into smaller chunks (e.g., 200 terms each)
python -c "
import json
with open('bulk_translations_simple.json', 'r') as f:
    data = json.load(f)

chunk_size = 200
for i in range(0, len(data), chunk_size):
    chunk = data[i:i+chunk_size]
    with open(f'chunk_{i//chunk_size + 1}.json', 'w') as f:
        json.dump(chunk, f, indent=2, ensure_ascii=False)
print(f'Created {(len(data) + chunk_size - 1) // chunk_size} chunks')
"
```

### Step 4: Merge Results (if chunked)

```bash
# Merge completed chunks back
python -c "
import json
chunks = []
i = 1
while True:
    try:
        with open(f'chunk_{i}_completed.json', 'r') as f:
            chunks.extend(json.load(f))
        i += 1
    except FileNotFoundError:
        break

# Update the main file
with open('bulk_translations.json', 'r') as f:
    main_data = json.load(f)

for item in chunks:
    pali = item['pali']
    if pali in main_data['translations']:
        main_data['translations'][pali]['english'] = item['english']
        main_data['translations'][pali]['sinhala'] = item['sinhala']

with open('bulk_translations.json', 'w') as f:
    json.dump(main_data, f, indent=2, ensure_ascii=False)
print('Merged all translations!')
"
```

### Step 5: Apply Translations

```bash
python apply_bulk_translations.py
```

## 💡 Pro Tips

### For Best Translation Quality:

1. **Use Buddhist context**: Mention these are canonical Buddhist terms
2. **Provide examples**: Show a few completed translations as examples
3. **Be specific about terminology**:
   - `suttaṃ` = discourse/teaching
   - `vaggo` = chapter/section  
   - `saṃyuttaṃ` = connected discourses
   - `nipāto` = collection

### Sample Prompt Enhancement:
```
Context: These are Pali terms from the Buddhist Tipitaka (canonical texts).

Translation guidelines:
- "suttaṃ" endings: These are discourse titles (e.g., "Bhikkhusuttaṃ" = "The Discourse to Monks")
- "vaggo" endings: These are chapter names (e.g., "Dutiyavaggo" = "Second Chapter")
- "saṃyuttaṃ" endings: Connected discourses (e.g., "Kassapasaṃyuttaṃ" = "Connected Discourses with Kassapa")

Please maintain consistency with standard Buddhist English terminology.
```

## 🔄 Alternative: Manual Editing

If you prefer manual control:

1. Open `bulk_translations_simple.json` in a text editor
2. Fill in translations manually
3. Use find-replace for common patterns:
   - `"vaggo"` → `"Chapter"`
   - `"suttaṃ"` → `"Discourse"`
4. Save and run `python apply_bulk_translations.py`

## ⚡ Speed Comparison

| Method | Time Required | Effort |
|--------|---------------|---------|
| **Daily batches** | 162 days | 5-10 min/day |
| **Bulk translation** | 1-2 hours | One session |

## 🎉 Final Step

After completing translations:

```bash
# Apply all translations
python apply_bulk_translations.py

# Verify (should show 0 missing)
python create_bulk_translation_json.py

# Import to database
python import_to_turso_updated.py
```

---

**Result**: Complete multilingual Buddhist text database in hours instead of months! 🚀