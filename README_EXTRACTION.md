# Pali PDF Extraction Tool

A generalized script for extracting Pali text from Dīgha Nikāya PDFs and creating structured JSON files for translation.

## Features

✅ **Generalized Extraction**: Works with any Dīgha Nikāya PDF
✅ **Auto-Detection**: Automatically detects chapters from PDF content
✅ **Chapter Splitting**: Correctly splits chapters (no more "everything in the last chapter" issue)
✅ **Section Renumbering**: Renumbers sections to start from 1 for each chapter
✅ **PaliTitle Detection**: Extracts section titles (paliTitle) using multiple methods:
  - Pattern-based detection (vatthu, kathā, vaṇṇanā, etc.)
  - Bold text detection from PDF formatting
  - Context-aware filtering
✅ **Clean Text**: Removes metadata (page numbers, URLs, etc.)
✅ **UTF-8 Support**: Properly handles all Pali diacritical marks

## Usage

### Basic Usage

```python
python extract_pali_pdf.py
```

### Custom Configuration

Edit the `main()` function in `extract_pali_pdf.py`:

```python
book_config = {
    'name': 'Sīlakkhandhavaggapāḷi',           # Output folder name
    'pali_title': 'Sīlakkhandhavaggapāḷi',     # Pali book title
    'english_title': 'The Division of...',      # English title (optional)
    'sinhala_title': '',                         # Sinhala title (optional)
    'starting_dn': 1,                            # Starting DN number (DN 1, DN 14, etc.)
    'chapters': [],                              # Auto-detect if empty
    'renumber_sections': True                    # Renumber sections from 1 per chapter
}
```

### For Different Books

#### Example: Mahāvaggapāḷi (DN 14-16)
```python
book_config = {
    'name': 'Mahāvaggapāḷi',
    'pali_title': 'Mahāvaggapāḷi',
    'starting_dn': 14,
    'chapters': [],  # Will auto-detect DN 14, 15, 16
    'renumber_sections': False  # Keep original continuous numbering
}
```

#### Example: Pāthikavaggapāḷi (DN 24-34)
```python
book_config = {
    'name': 'Pāthikavaggapāḷi',
    'pali_title': 'Pāthikavaggapāḷi',
    'starting_dn': 24,
    'chapters': [],
    'renumber_sections': True
}
```

## Output Structure

```
BookName/
├── book.json                           # Book metadata
├── BookName_pali_extracted.txt        # Full extracted Pali text
└── chapters/
    ├── dn1-ChapterName.json           # Chapter 1
    ├── dn2-ChapterName.json           # Chapter 2
    └── ...
```

## JSON Structure

### book.json
```json
{
  "name": "Sīlakkhandhavaggapāḷi",
  "title": {
    "pali": "Sīlakkhandhavaggapāḷi",
    "english": "The Division of the Moral Precepts",
    "sinhala": ""
  },
  "chapters": [
    {
      "id": "dn1",
      "title": {
        "pali": "Brahmajālasuttaṃ",
        "english": "",
        "sinhala": ""
      }
    }
  ]
}
```

### Chapter JSON (e.g., dn1-Brahmajālasuttaṃ.json)
```json
{
  "id": "dn1",
  "title": {
    "pali": "Brahmajālasuttaṃ",
    "english": "",
    "sinhala": ""
  },
  "sections": [
    {
      "number": 1,
      "pali": "Evaṃ me sutaṃ...",
      "english": "",
      "sinhala": "",
      "paliTitle": "Paribbājakakathā"
    }
  ]
}
```

## Extraction Results

### Sīlakkhandhavaggapāḷi
- **PDF Pages**: 117
- **Chapters**: 13 (DN 1-13)
- **Total Sections**: 559
- **Chapters**:
  1. DN 1: Brahmajālasuttaṃ (149 sections)
  2. DN 2: Sāmaññaphalasuttaṃ (104 sections)
  3. DN 3: Ambaṭṭhasuttaṃ (46 sections)
  4. DN 4: Soṇadaṇḍasuttaṃ (23 sections)
  5. DN 5: Kūṭadantasuttaṃ (36 sections)
  6. DN 6: Mahālisuttaṃ (19 sections)
  7. DN 7: Jāliyasuttaṃ (3 sections)
  8. DN 8: Mahāsīhanādasuttaṃ (25 sections)
  9. DN 9: Poṭṭhapādasuttaṃ (38 sections)
  10. DN 10: Subhasuttaṃ (37 sections)
  11. DN 11: Kevaṭṭasuttaṃ (20 sections)
  12. DN 12: Lohiccasuttaṃ (17 sections)
  13. DN 13: Tevijjasuttaṃ (42 sections)

## Fixes from Previous Version

### 1. ✅ Chapter Splitting Issue - FIXED
**Problem**: In `extract_mahavaggapali.py`, chapters were not split correctly. The first 2 chapters were fine, but everything else ended up in the 3rd chapter.

**Solution**: 
- More precise regex matching for chapter boundaries
- Uses exact chapter number + title matching: `^{number}\.\s+{title}\s*$`
- Prevents false positives from similar text patterns

### 2. ✅ Section Renumbering - ADDED
**Problem**: Original PDFs have continuous section numbering across all chapters (e.g., Chapter 2 starts with section 150).

**Solution**:
- Added `renumber_sections` configuration option
- When enabled (default), renumbers sections to start from 1 for each chapter
- Can be disabled to preserve original continuous numbering

### 3. ✅ PaliTitle Detection - IMPROVED
**Problem**: Section titles (paliTitle) were not reliably detected.

**Solution**:
- Added PDF formatting analysis to detect bold text
- Enhanced pattern matching for common title endings
- Better context filtering to avoid false positives
- Example detected titles: "Paribbājakakathā", "Rājāmaccakathā", "Cūḷasīla", etc.

## Requirements

```bash
pip install PyMuPDF  # fitz
```

## Notes

- The script preserves all Pali diacritical marks (ā, ḍ, ṃ, ṭ, ñ, etc.)
- Metadata is automatically removed (page numbers, URLs, organization names)
- Works on Windows with proper UTF-8 encoding
- Empty `english` and `sinhala` fields are ready for translation

## Comparison with Old Script

| Feature | extract_mahavaggapali.py | extract_pali_pdf.py (NEW) |
|---------|--------------------------|---------------------------|
| Book-specific | ✅ Mahāvaggapāḷi only | ❌ Works with any DN book |
| Chapter splitting | ⚠️ Had issues | ✅ Fixed with precise matching |
| Auto-detection | ❌ Manual config | ✅ Auto-detects chapters |
| Section renumbering | ❌ No | ✅ Yes (configurable) |
| PaliTitle detection | ⚠️ Basic patterns | ✅ Patterns + bold detection |
| Configuration | ❌ Hardcoded | ✅ Flexible config dict |

## Future Enhancements

- [ ] Support for other Nikāyas (Majjhima, Saṃyutta, Aṅguttara)
- [ ] GUI for configuration
- [ ] Batch processing for multiple PDFs
- [ ] Translation validation tools

