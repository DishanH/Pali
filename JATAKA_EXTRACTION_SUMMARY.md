# Jātakapāḷi Extraction Summary

## Overview
Successfully extracted both Jātakapāḷi volumes (1 and 2) into a combined folder structure with proper handling of the unique 3-level hierarchy.

## Structure

### Jātakapāḷi Hierarchy
The Jātakapāḷi has a unique structure compared to other Nikāyas:

**Volume 1 (Nipātas 1-16):**
- **Nipāta** (e.g., "1. Ekakanipāto") - Main division
- **Vagga** (e.g., "1. Apaṇṇakavaggo") - Sub-chapter (becomes the JSON chapter)
- **Jātaka** (e.g., "1. Apaṇṇakajātakaṃ") - Individual story (becomes a section)

**Volume 2 (Nipātas 17-22):**
- **Nipāta** (e.g., "17. Cattālīsanipāto") - Main division (becomes the JSON chapter)
- **Jātaka** (e.g., "521. Tesakuṇajātakaṃ (1)") - Individual story (becomes a section)

## Output Structure

### Directory Layout
```
Khuddakanikāye/Jātakapāḷi/
├── chapters/
│   ├── ja.1-Apaṇṇakavaggo.json
│   ├── ja.2-Sīlavaggo.json
│   ├── ...
│   ├── ja.42-Gandhāravaggo.json
│   ├── ja.43-Cattālīsanipāto.json
│   ├── ja.44-Paṇṇāsanipāto.json
│   ├── ...
│   └── ja.48-Mahānipāto.json
├── book.json
├── Jātakapāḷi_1_pali_extracted.txt
└── Jātakapāḷi_2_pali_extracted.txt
```

### JSON Structure

#### Early Vaggas (ja.1 - ja.42)
```json
{
  "id": "ja.1",
  "title": {
    "pali": "Apaṇṇakavaggo",
    "english": "",
    "sinhala": ""
  },
  "sections": [
    {
      "number": 1,
      "pali": "...",
      "english": "",
      "sinhala": "",
      "paliTitle": "Apaṇṇakajātakaṃ",
      "nipataTitle": "Ekakanipāto"
    },
    {
      "number": 2,
      "pali": "...",
      "english": "",
      "sinhala": "",
      "paliTitle": "Vaṇṇupathajātakaṃ"
    }
  ],
  "footer": {
    "pali": "",
    "english": "",
    "sinhala": ""
  }
}
```

#### Later Nipātas (ja.43 - ja.48)
```json
{
  "id": "ja.43",
  "title": {
    "pali": "Cattālīsanipāto",
    "english": "",
    "sinhala": ""
  },
  "sections": [
    {
      "number": 1,
      "pali": "...",
      "english": "",
      "sinhala": "",
      "paliTitle": "Tesakuṇajātakaṃ",
      "nipataTitle": "Cattālīsanipāto",
      "paliMainTitle": "521. Tesakuṇajātakaṃ"
    },
    {
      "number": 2,
      "pali": "...",
      "english": "",
      "sinhala": "",
      "paliTitle": "Tesakuṇajātakaṃ",
      "paliMainTitle": "521. Tesakuṇajātakaṃ"
    }
  ],
  "footer": {
    "pali": "",
    "english": "",
    "sinhala": ""
  }
}
```

## Key Features

### 1. Dual Structure Support
- **Early volumes (1-16)**: Vaggas are used as chapters, with nipāta information preserved
- **Later volumes (17-22)**: Nipātas themselves become chapters

### 2. Jātaka Identification
- **Early volumes**: `paliTitle` contains the Jātaka name (e.g., "Apaṇṇakajātakaṃ")
- **Later volumes**: 
  - `paliTitle` contains the Jātaka name
  - `paliMainTitle` contains the full numbered title (e.g., "521. Tesakuṇajātakaṃ")

### 3. Nipāta Information in First Section Only
- The `nipataTitle` field appears **only in the first section** of each chapter
- This avoids duplication while preserving the hierarchical context
- Format: `"nipataTitle": "Ekakanipāto"` (simple string, not an object)

### 4. Continuous Chapter IDs
- Chapters are numbered continuously from ja.1 to ja.48
- Volume 2 chapters continue from where Volume 1 ended

## Statistics

### Volume 1 (Jātakapāḷi_1)
- **Pages**: 238
- **Chapters**: 42 vaggas
- **Nipātas**: 16 (Ekakanipāto through Tiṃsanipāto)

### Volume 2 (Jātakapāḷi_2)
- **Pages**: 233
- **Chapters**: 6 nipātas
- **Nipātas**: 6 (Cattālīsanipāto through Mahānipāto)

### Combined
- **Total Chapters**: 48
- **Total Pages**: 471

## Scripts Created

### 1. extract_jataka_correct.py
Main extractor class that handles:
- PDF text extraction
- Structure detection (nipāta/vagga/jātaka)
- Dual structure support (vagga-based vs nipāta-based)
- JSON generation with proper metadata

### 2. extract_jataka_batch.py
Batch processor that:
- Processes both volumes sequentially
- Combines output into single folder
- Adjusts chapter IDs for continuity
- Creates combined book.json

## Usage

### Extract Both Volumes
```bash
python extract_jataka_batch.py
```

### Extract Single Volume (for testing)
```bash
python extract_jataka_correct.py
```

## Notes

1. **Nipāta Information**: All chapters preserve their nipāta information, making it easy to understand the hierarchical structure
2. **Jātaka Numbers**: Later volumes include the original Jātaka numbers (521+) in the `paliMainTitle` field
3. **Combined Output**: Both volumes are merged into a single `Jātakapāḷi` folder for easier management
4. **Continuous IDs**: Chapter IDs run from ja.1 to ja.48 without gaps

## Next Steps

The extracted JSON files are now ready for:
1. Translation using the translator.py script
2. Integration with the mobile app
3. Further processing or validation as needed
