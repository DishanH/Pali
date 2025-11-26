# PDF Extraction Guide for Tipitaka Collections

This guide covers extracting PDFs from **Majjhima Nikāya**, **Saṃyutta Nikāya**, and **Khuddaka Nikāya** collections, similar to the Aṅguttara and Dīgha Nikāya extractions already completed.

## Overview

Each Nikāya collection has two scripts:
- **`extract_<nikaya>_correct.py`** - Single file extraction (for testing)
- **`extract_<nikaya>_batch.py`** - Batch extraction (processes all PDFs in the collection)

## Available Collections

### 1. Majjhima Nikāya (3 books)
- **Mūlapaṇṇāsapāḷi** - First 50 suttas
- **Majjhimapaṇṇāsapāḷi** - Second 50 suttas  
- **Uparipaṇṇāsapāḷi** - Last 52 suttas (152 total)

### 2. Saṃyutta Nikāya (5 vaggas)
- **Sagāthāvaggo** - With verses
- **Nidānavaggo** - Causation
- **Khandhavaggo** - Aggregates
- **Saḷāyatanavaggo** - Six sense bases
- **Mahāvaggo** - Great chapter

### 3. Khuddaka Nikāya (21 books)
- **Khuddakapāṭhapāḷi** - Short readings
- **Dhammapadapāḷi** - Verses of Dhamma
- **Udānapāḷi** - Inspired utterances
- **Itivuttakapāḷi** - Thus said discourses
- **Suttanipātapāḷi** - Collection of suttas
- **Vimānavatthupāḷi** - Stories of mansions
- **Petavatthupāḷi** - Stories of ghosts
- **Theragāthāpāḷi** - Verses of elder monks
- **Therīgāthāpāḷi** - Verses of elder nuns
- **Jātakapāḷi** (1 & 2) - Birth stories
- **Mahāniddesapāḷi** - Great exposition
- **Cūḷaniddesapāḷi** - Small exposition
- **Paṭisambhidāmaggapāḷi** - Path of discrimination
- **Therāpadānapāḷi** (1 & 2) - Chronicles of elders
- **Buddhavaṃsapāḷi** - Chronicle of Buddhas
- **Cariyāpiṭakapāḷi** - Basket of conduct
- **Nettippakaraṇapāḷi** - Guide
- **Peṭakopadesapāḷi** - Basket instruction
- **Milindapañhapāḷi** - Questions of King Milinda

## Quick Start

### Extract All Books from a Collection

```bash
# Extract all Majjhima Nikāya PDFs
python extract_majjhima_batch.py

# Extract all Saṃyutta Nikāya PDFs
python extract_samyutta_batch.py

# Extract all Khuddaka Nikāya PDFs
python extract_khuddaka_batch.py
```

### Extract a Single Book (for testing)

```bash
# Test single Majjhima book
python extract_majjhima_correct.py

# Test single Saṃyutta book
python extract_samyutta_correct.py

# Test single Khuddaka book
python extract_khuddaka_correct.py
```

## Output Structure

Each extraction creates:

```
<Collection>/<Book>/
├── book.json                          # Book metadata
├── chapters/                          # Chapter JSON files
│   ├── <id>-<title>.json
│   ├── <id>-<title>.json
│   └── ...
└── <Book>_pali_extracted.txt         # Full extracted text
```

### JSON Structure

Each chapter JSON follows this format:

```json
{
  "id": "mn.1.1",
  "title": {
    "pali": "Chapter title in Pali",
    "english": "",
    "sinhala": ""
  },
  "sections": [
    {
      "number": 1,
      "pali": "Pali text content...",
      "english": "",
      "sinhala": "",
      "paliTitle": "Optional sutta title"
    }
  ],
  "footer": {
    "pali": "",
    "english": "",
    "sinhala": ""
  }
}
```

## Directory Requirements

PDFs must be organized as follows:

```
Majjhimanikāye/
└── pdfs/
    ├── Mūlapaṇṇāsapāḷi.pdf
    ├── Majjhimapaṇṇāsapāḷi.pdf
    └── Uparipaṇṇāsapāḷi.pdf

Saṃyuttanikāyo/
└── pdfs/
    ├── Sagāthāvaggo.pdf
    ├── Nidānavaggo.pdf
    ├── Khandhavaggo.pdf
    ├── Saḷāyatanavaggo.pdf
    └── Mahāvaggo.pdf

Khuddakanikāye/
└── pdfs/
    ├── Khuddakapāṭhapāḷi.pdf
    ├── Dhammapadapāḷi.pdf
    ├── ... (21 PDFs total)
```

## ID Prefixes

Each collection uses standardized ID prefixes:

### Majjhima Nikāya
- Format: `mn.<book>.<chapter>`
- Example: `mn.1.1` (Mūlapaṇṇāsapāḷi, Chapter 1)

### Saṃyutta Nikāya  
- Format: `sn.<vagga>.<samyutta>`
- Example: `sn.1.1` (Sagāthāvaggo, Devatāsaṃyuttaṃ)

### Khuddaka Nikāya
- Format: `<prefix>.<chapter>`
- Examples:
  - `dhp.1` (Dhammapada, Chapter 1)
  - `ud.1` (Udāna, Chapter 1)
  - `snp.1` (Sutta Nipāta, Chapter 1)

## Customizing Single File Extraction

To test a different book, edit the `main()` function in the `*_correct.py` script:

### Majjhima Example
```python
book_config = {
    'name': 'Majjhimapaṇṇāsapāḷi',
    'pali_title': 'Majjhimapaṇṇāsapāḷi',
    'english_title': '',
    'sinhala_title': '',
    'book_num': 2,  # Second book
}

pdf_path = r"Majjhimanikāye\pdfs\Majjhimapaṇṇāsapāḷi.pdf"
output_dir = r"Majjhimanikāye\Majjhimapaṇṇāsapāḷi"
```

### Saṃyutta Example
```python
book_config = {
    'name': 'Nidānavaggo',
    'pali_title': 'Nidānavaggo',
    'english_title': '',
    'sinhala_title': '',
    'vagga_num': 2,  # Second vagga
}

pdf_path = r"Saṃyuttanikāyo\pdfs\Nidānavaggo.pdf"
output_dir = r"Saṃyuttanikāyo\Nidānavaggo"
```

### Khuddaka Example
```python
book_config = {
    'name': 'Udānapāḷi',
    'pali_title': 'Udānapāḷi',
    'english_title': '',
    'sinhala_title': '',
    'id_prefix': 'ud',
}

pdf_path = r"Khuddakanikāye\pdfs\Udānapāḷi.pdf"
output_dir = r"Khuddakanikāye\Udānapāḷi"
```

## Text Structure Detection

Each extractor automatically detects structure patterns:

### Majjhima Nikāya
- **Vaggas**: `1. Mūlapariyāyavaggo`
- **Suttas**: `1. Mūlapariyāyasuttaṃ`
- **Sections**: `1. Evaṃ me sutaṃ...`

### Saṃyutta Nikāya
- **Saṃyuttas**: `1. Devatāsaṃyuttaṃ`
- **Vaggas** (within saṃyutta): `1. Naḷavaggo`
- **Suttas**: `1. Oghataraṇasuttaṃ`
- **Sections**: `1. Evaṃ me sutaṃ...`

### Khuddaka Nikāya (varied)
- **Vaggas**: `1. Yamakavaggo`
- **Nipātas**: `1. Uragavaggo` (Sutta Nipāta)
- **Vatthu**: `1. Upakāravatthu` (Vimānavatthu/Petavatthu)
- **Verses**: Numbered verses or sections

## Error Handling

The batch scripts handle errors gracefully:
- **Skips** missing PDFs (with warning)
- **Continues** processing after errors
- **Reports** summary at the end

Example output:
```
✅ Successful: 3/3
❌ Failed: 0/3
⚠️  Skipped: 0/3
```

## Requirements

All scripts require:
- **Python 3.7+**
- **PyMuPDF** (fitz): `pip install PyMuPDF`
- **UTF-8** encoding support (handled automatically on Windows)

## Troubleshooting

### Issue: "PDF file not found"
**Solution**: Verify PDF is in the correct `pdfs/` directory with exact filename

### Issue: "No chapters detected"
**Solution**: The extractor will create a single chapter with all content. Check if the PDF has unusual structure.

### Issue: Unicode encoding errors (Windows)
**Solution**: Already handled by scripts with `sys.stdout.reconfigure(encoding='utf-8')`

## Post-Extraction

After extraction, use existing translation tools:

```bash
# Translate chapters
python translate_json_chapters.py

# Translate titles and footers
python translate_titles_and_footer.py

# Verify translations
python verify_translations.py
```

## Related Scripts

- **Aṅguttara Nikāya**: `extract_anguttara_batch.py`
- **Dīgha Nikāya**: Use `extract_pali_pdf.py` with configs

## Summary

| Collection | Books | Batch Script | Single Script |
|------------|-------|--------------|---------------|
| Majjhima | 3 | `extract_majjhima_batch.py` | `extract_majjhima_correct.py` |
| Saṃyutta | 5 | `extract_samyutta_batch.py` | `extract_samyutta_correct.py` |
| Khuddaka | 21 | `extract_khuddaka_batch.py` | `extract_khuddaka_correct.py` |

---

**Note**: All scripts preserve the exact Pali text from PDFs and create empty placeholders for English and Sinhala translations to be filled by translation scripts.

