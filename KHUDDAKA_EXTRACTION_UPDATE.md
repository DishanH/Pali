# Khuddaka Nikāya Extraction Update

## Summary

Updated the Khuddaka Nikāya PDF extraction scripts to properly handle section titles (`paliTitle`) and conditionally include `vagga` information only when it differs from the chapter title.

## Changes Made

### 1. Updated `extract_khuddaka_correct.py`

Modified the `extract_sections_from_chapter()` method to:
- Accept the chapter title as a parameter
- Detect vagga markers within chapters (e.g., "1. Yamakavaggo", "2. Appamādavaggo")
- Track the current vagga throughout the chapter
- **Only include the `vagga` field when it differs from the chapter title** (avoids redundancy since each JSON file represents one vagga/chapter)
- Properly detect section titles (like "Akitticariyā", "Ratanacaṅkamanakaṇḍaṃ", "Paṭhamabodhisuttaṃ") and assign them to `paliTitle` instead of creating separate section nodes
- Skip header lines (Namo, Khuddakanikāye, book title) to avoid creating unnecessary sections

### 2. Updated `extract_khuddaka_batch.py`

Modified to skip Buddhavaṃsapāḷi (manually fixed by user)

### 2. Section Structure

Each section now includes the following fields:
```json
{
  "number": <section_number>,
  "pali": "<pali_text>",
  "english": "",
  "sinhala": "",
  "paliTitle": "<optional_sutta_title>",
  "vagga": "<vagga_name>",
  "numberRange": "<optional_range>"  // Only when applicable (e.g., "20-24")
}
```

### 3. Vagga Behavior

- **Dhammapada**: Each chapter (e.g., "Yamakavaggo") is itself a vagga, and all sections within that chapter have `vagga: "Yamakavaggo"`
- **Udāna**: Similar to Dhammapada - chapter title is the vagga
- **Sutta Nipāta**: Chapter title (e.g., "Uragavaggo") is the vagga
- **Itivuttaka**: Each chapter (e.g., "Paṭhamavaggo") is the vagga
- **Other texts**: Follow the same pattern - chapter title serves as the vagga

### 4. Number Ranges

Some texts (like Paṭisambhidāmagga) have sections with number ranges (e.g., "20-24. Ñāṇapañcakaniddeso"). These are now captured with:
- `number`: The starting number (e.g., 20)
- `numberRange`: The full range (e.g., "20-24")

## Batch Extraction Results

Successfully extracted all 21 Khuddaka Nikāya texts:
1. Khuddakapāṭhapāḷi
2. Dhammapadapāḷi
3. Udānapāḷi
4. Itivuttakapāḷi
5. Suttanipātapāḷi
6. Vimānavatthupāḷi
7. Petavatthupāḷi
8. Theragāthāpāḷi
9. Therīgāthāpāḷi
10. Jātakapāḷi_1
11. Jātakapāḷi_2
12. Mahāniddesapāḷi
13. Cūḷaniddesapāḷi
14. Paṭisambhidāmaggapāḷi
15. Therāpadānapāḷi_1
16. Therāpadānapāḷi_2
17. Buddhavaṃsapāḷi
18. Cariyāpiṭakapāḷi
19. Nettippakaraṇapāḷi
20. Peṭakopadesapāḷi
21. Milindapañhapāḷi

## Example Output

### Dhammapada (dhp.1-Yamakavaggo.json)
**No `vagga` field** - since the vagga is the same as the chapter title
```json
{
  "id": "dhp.1",
  "title": {
    "pali": "Yamakavaggo",
    "english": "",
    "sinhala": ""
  },
  "sections": [
    {
      "number": 1,
      "pali": "Manopubbaṅgamā dhammā...",
      "english": "",
      "sinhala": "",
      "paliTitle": ""
    },
    ...
  ]
}
```

### Cariyāpiṭakapāḷi (with paliTitle)
**No `vagga` field** - since the vagga is the same as the chapter title
```json
{
  "number": 1,
  "pali": "''Kappe ca satasahasse...",
  "english": "",
  "sinhala": "",
  "paliTitle": "Akitticariyā"
}
```

### Udāna (with paliTitle)
**No `vagga` field** - since the vagga is the same as the chapter title
```json
{
  "number": 1,
  "pali": "Evaṃ me sutaṃ – ekaṃ samayaṃ...",
  "english": "",
  "sinhala": "",
  "paliTitle": "Paṭhamabodhisuttaṃ"
}
```

### Example with Sub-Vagga (if applicable)
**`vagga` field included** - only when sub-vagga differs from chapter title
```json
{
  "id": "example.1",
  "title": {
    "pali": "Main Chapter Title",
    "english": "",
    "sinhala": ""
  },
  "sections": [
    {
      "number": 1,
      "pali": "Content...",
      "english": "",
      "sinhala": "",
      "paliTitle": "",
      "vagga": "Sub-Vagga Name"
    }
  ]
}
```

## Files Modified

1. `extract_khuddaka_correct.py` - Main extraction script
2. All JSON files in `Khuddakanikāye/*/chapters/*.json` - Regenerated with vagga field

## Notes

- Section numbering resets within each vagga (as observed in the original PDFs)
- The `vagga` field provides context for which vagga/chapter a section belongs to
- This structure is now consistent with Saṃyuttanikāyo for easier cross-referencing
- All existing fields (pali, english, sinhala, paliTitle) are preserved

