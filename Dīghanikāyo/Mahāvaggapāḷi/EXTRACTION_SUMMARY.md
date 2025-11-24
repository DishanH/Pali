# Mahāvaggapāḷi Extraction Summary

## Overview
Successfully extracted Pali text from Mahāvaggapāḷi PDF and created structured JSON files.

## Output Structure
```
Mahāvaggapāḷi/
├── book.json                              # Book metadata
├── Mahāvaggapāḷi_pali_extracted.txt      # Full extracted text
├── chapters/
│   ├── dn14-Mahāpadānasuttaṃ.json        # 94 sections (1-94)
│   ├── dn15-Mahānidānasuttaṃ.json         # 36 sections (95-130)
│   └── dn16-Mahāparinibbānasuttaṃ.json    # 308 sections (131-438+)
└── EXTRACTION_SUMMARY.md                  # This file
```

## Extraction Details

### Chapters Extracted
1. **Mahāpadānasuttaṃ** (DN 14)
   - Sections: 94 (numbered 1-94)
   - Notable paliTitles:
     - Section 1: "Pubbenivāsapaṭisaṃyuttakathā"
     - Section 17: "Bodhisattadhammatā"
     - Section 33: "Dvattiṃsamahāpurisalakkhaṇā"
     - Section 45: "Brahmayācanakathā"

2. **Mahānidānasuttaṃ** (DN 15)
   - Sections: 36 (numbered 95-130)
   - Notable paliTitles:
     - Section 117: "Attapaññatti"
     - Section 119: "Naattapaññatti"
     - Section 121: "Attasamanupassanā"
     - Section 127: "Satta viññāṇaṭṭhiti"
     - Section 129: "Aṭṭha vimokkhā"

3. **Mahāparinibbānasuttaṃ** (DN 16)
   - Sections: 308 (numbered 131+)
   - This is the famous Mahāparinibbāna Sutta describing the Buddha's final days
   - Contains many subsections with paliTitles

### Section Numbering
**Important Note**: The section numbers in the source text are continuous across the entire Mahāvaggapāḷi, not starting from 1 for each chapter. This is the original numbering system and has been preserved:
- Mahāpadānasuttaṃ: sections 1-94
- Mahānidānasuttaṃ: sections 95-130
- Mahāparinibbānasuttaṃ: sections 131-438+

## Features

### Text Cleaning
✅ Removed metadata:
- Page numbers (e.g., "Page 1 sur 144")
- Website URLs (www.tipitaka.org)
- Organization name (Vipassana Research Institute)
- Standalone numbers

✅ Preserved:
- All Pali text without unwanted spaces in words
- Proper diacritical marks (ā, ḍ, ṃ, ṭ, ñ, etc.)
- Editorial notes in square brackets

### paliTitle Detection
The script automatically detects section titles (paliTitle) based on:
- Lines ending with common patterns (vatthu, kathā, vaṇṇanā, dhammā, etc.)
- Short lines (< 100 characters)
- No sentence punctuation (commas, quotes, etc.)
- Placed immediately before numbered sections

### JSON Structure
Each chapter JSON follows the template structure:
```json
{
  "id": "dn14",
  "title": {
    "pali": "Mahāpadānasuttaṃ",
    "english": "",
    "sinhala": ""
  },
  "sections": [
    {
      "number": 1,
      "pali": "...",
      "english": "",
      "sinhala": "",
      "paliTitle": "Pubbenivāsapaṭisaṃyuttakathā"
    }
  ]
}
```

## Usage

### Translation Workflow
1. Use the generated JSON files as input for translation
2. Fill in the `english` and `sinhala` fields for titles and sections
3. The `pali` field contains the source text
4. The `paliTitle` field indicates section headings when present

### Files Generated
- **book.json**: Metadata about the Mahāvaggapāḷi collection with chapter information
- **Mahāvaggapāḷi_pali_extracted.txt**: Full extracted Pali text for reference
- **chapters/*.json**: Individual chapter files ready for translation

## Script Information
- **Script**: `extract_mahavaggapali.py`
- **Dependencies**: PyMuPDF (fitz)
- **Extraction Date**: 2025-11-10
- **Source**: Mahāvaggapāḷi.pdf (144 pages)

## Statistics
- **Total Pages Processed**: 144
- **Total Lines Extracted**: 6,062
- **Total Chapters**: 3
- **Total Sections**: 438+
- **Text Format**: UTF-8
- **No newline characters in output** (as requested)

## Notes
- The extraction preserves the original continuous section numbering across all chapters
- Empty `paliTitle` fields indicate sections without specific titles
- All Pali diacritics are properly preserved
- The script can be rerun if needed to regenerate the files

