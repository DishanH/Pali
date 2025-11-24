# Complete Diagnosis and Fix for Translation Issues

## What Happened?

When you ran `python fix_and_retranslate.py dn2 dn4 dn5`, here's what actually occurred:

### The Log Reveals:
- ✅ The script started correctly
- ❌ **Only dn5 was processed** (dn2 and dn4 were skipped/failed silently)
- ❌ When translating dn5's title "Sampasādanīyasuttaṃ" (19 chars), the AI expanded it to **17,931 characters**!

### Why This Happened:

1. **Title Translation is Too Open-Ended**: The current prompt allows the AI to "elaborate" on titles, turning a simple title like "Sampasādanīyasuttaṃ" into a full essay/introduction.

2. **Section Numbers Removal Works**: The regex I added does remove numbers like "1.", "49.", "10 ." from translated text.

3. **But Title Expansion Bypasses This**: Because the title itself is being replaced with massive content, removing numbers doesn't help.

## The Core Problem

Looking at the current code in `translator.py` (lines 414-416):

```python
'title': {
    'pali': chapter_title,
    'english': self.translate_text(chapter_title, 'English'),  # ← This is the problem!
    'sinhala': self.translate_text(chapter_title, 'Sinhala')   # ← This too!
}
```

The `translate_text()` method uses a general translation prompt that doesn't constrain the AI to ONLY translate the title.

## The Solution

### Step 1: Update `book.json` with Correct Title Translations

Add the English and Sinhala translations directly to `book.json`:

```json
{
  "chapters": [
    {
      "id": "dn1",
      "title": {
        "pali": "Pāthikasuttaṃ",
        "english": "The Pāthika Discourse",
        "sinhala": "පාඨික සූත්‍රය"
      }
    },
    {
      "id": "dn2",
      "title": {
        "pali": "Udumbarikasuttaṃ",
        "english": "The Udumbarika Discourse",
        "sinhala": "උදුම්බරික සූත්‍රය"
      }
    },
    {
      "id": "dn3",
      "title": {
        "pali": "Cakkavattisuttaṃ",
        "english": "The Wheel-Turning Monarch Discourse",
        "sinhala": "චක්‍රවත්ති සූත්‍රය"
      }
    },
    {
      "id": "dn4",
      "title": {
        "pali": "Aggaññasuttaṃ",
        "english": "The Discourse on Origins",
        "sinhala": "අග්ගඤ්ඤ සූත්‍රය"
      }
    },
    {
      "id": "dn5",
      "title": {
        "pali": "Sampasādanīyasuttaṃ",
        "english": "The Inspiring Confidence Discourse",
        "sinhala": "සම්ප්‍රසාදනීය සූත්‍රය"
      }
    },
    {
      "id": "dn6",
      "title": {
        "pali": "Pāsādikasuttaṃ",
        "english": "The Delightful Discourse",
        "sinhala": "පාසාදික සූත්‍රය"
      }
    },
    {
      "id": "dn7",
      "title": {
        "pali": "Lakkhaṇasuttaṃ",
        "english": "The Discourse on Marks",
        "sinhala": "ලක්ඛණ සූත්‍රය"
      }
    },
    {
      "id": "dn9",
      "title": {
        "pali": "Āṭānāṭiyasuttaṃ",
        "english": "The Āṭānāṭiya Discourse",
        "sinhala": "ආටානාටිය සූත්‍රය"
      }
    },
    {
      "id": "dn10",
      "title": {
        "pali": "Saṅgītisuttaṃ",
        "english": "The Discourse on the Communal Recitation",
        "sinhala": "සංගීති සූත්‍රය"
      }
    },
    {
      "id": "dn11",
      "title": {
        "pali": "Dasuttarasuttaṃ",
        "english": "The Tenfold Discourse",
        "sinhala": "දසුත්තර සූත්‍රය"
      }
    }
  ]
}
```

### Step 2: Update `translator.py` to Use Titles from `book.json`

Modify the `translate_chapter` method:

```python
def translate_chapter(self, pali_text: str, chapter_id: str, chapter_title_pali: str, 
                     chapter_title_english: str = "", chapter_title_sinhala: str = "", 
                     resume_from: int = 0) -> Dict:
    """
    Translate an entire chapter from Pali to English and Sinhala
    
    Args:
        pali_text: The full Pali text of the chapter
        chapter_id: ID like 'dn1'
        chapter_title_pali: Pali title
        chapter_title_english: Pre-translated English title (from book.json)
        chapter_title_sinhala: Pre-translated Sinhala title (from book.json)
        resume_from: Section number to resume from
    """
    # ... existing code ...
    
    # Create chapter JSON structure
    chapter_json = {
        'id': chapter_id,
        'title': {
            'pali': chapter_title_pali,
            'english': chapter_title_english,  # Use provided translation
            'sinhala': chapter_title_sinhala   # Use provided translation
        },
        'sections': translated_sections
    }
    
    return chapter_json
```

### Step 3: Update Scripts to Pass Title Translations

Update `fix_and_retranslate.py` and `translator.py` main function:

```python
def fix_chapter(chapter_id: str, translator: PaliTranslator, pali_text: str, book_data: dict):
    # ... existing code to find chapter_info ...
    
    chapter_title_pali = chapter_info['title']['pali']
    chapter_title_english = chapter_info['title']['english']  # Get from book.json
    chapter_title_sinhala = chapter_info['title']['sinhala']  # Get from book.json
    
    # Translate the chapter
    chapter_json = translator.translate_chapter(
        pali_text=chapter_text,
        chapter_id=chapter_id,
        chapter_title_pali=chapter_title_pali,
        chapter_title_english=chapter_title_english,  # Pass it
        chapter_title_sinhala=chapter_title_sinhala    # Pass it
    )
```

## Why This Approach is Better

1. **No AI Hallucination**: Titles are manually verified and controlled
2. **Consistent Quality**: All titles follow the same format
3. **Faster**: No API calls needed for titles
4. **Reliable**: No risk of the AI adding extra content

## What You Need to Do

1. **Update `book.json`** with the title translations I provided above
2. **Update `translator.py`** with the modified `translate_chapter` signature
3. **Update `fix_and_retranslate.py`** to pass title translations
4. **Manually fix** the three JSON files (dn2, dn4, dn5) that currently have corrupted titles

### Quick Manual Fix for JSON Files

For each of dn2, dn4, dn5:

1. Open the file
2. Find the `"title"` section
3. Replace with:
   ```json
   "title": {
     "pali": "Udumbarikasuttaṃ",           // or Aggaññasuttaṃ, Sampasādanīyasuttaṃ
     "english": "The Udumbarika Discourse",  // or appropriate English
     "sinhala": "උදුම්බරික සූත්‍රය"        // or appropriate Sinhala
   }
   ```
4. Save the file

## Alternative: Quick Regex Fix (Temporary)

If you want a quick temporary fix without modifying the translator:

```python
# In clean_translation(), add:
# If translated text is suspiciously long compared to input, truncate
if len(text) > len(original_pali) * 10:  # More than 10x expansion is suspicious
    # This is likely AI hallucination, use only first paragraph
    text = text.split('\n\n')[0]
```

But this is NOT recommended as a permanent solution!

---

## Summary

The core issue is **AI title translation is uncontrolled and creates massive expansions**. The solution is to **use pre-defined title translations from `book.json`** instead of asking the AI to translate them.

This is actually a **best practice** for any AI translation system:
- Short, important phrases (like titles) → Manual/controlled translation
- Long content (like sections) → AI translation with strict prompts

Would you like me to:
1. Create an updated `book.json` with all title translations?
2. Modify `translator.py` to use those titles?
3. Create a quick script to fix the three corrupted JSON files?

