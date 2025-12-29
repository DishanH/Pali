# Translation Chunks

Original file split into 33 chunks of ~50 terms each.

## Files created:
- `chunk_01.json` (terms 1-50)
- `chunk_02.json` (terms 51-100)
- `chunk_03.json` (terms 101-150)
- `chunk_04.json` (terms 151-200)
- `chunk_05.json` (terms 201-250)
- `chunk_06.json` (terms 251-300)
- `chunk_07.json` (terms 301-350)
- `chunk_08.json` (terms 351-400)
- `chunk_09.json` (terms 401-450)
- `chunk_10.json` (terms 451-500)
- `chunk_11.json` (terms 501-550)
- `chunk_12.json` (terms 551-600)
- `chunk_13.json` (terms 601-650)
- `chunk_14.json` (terms 651-700)
- `chunk_15.json` (terms 701-750)
- `chunk_16.json` (terms 751-800)
- `chunk_17.json` (terms 801-850)
- `chunk_18.json` (terms 851-900)
- `chunk_19.json` (terms 901-950)
- `chunk_20.json` (terms 951-1000)
- `chunk_21.json` (terms 1001-1050)
- `chunk_22.json` (terms 1051-1100)
- `chunk_23.json` (terms 1101-1150)
- `chunk_24.json` (terms 1151-1200)
- `chunk_25.json` (terms 1201-1250)
- `chunk_26.json` (terms 1251-1300)
- `chunk_27.json` (terms 1301-1350)
- `chunk_28.json` (terms 1351-1400)
- `chunk_29.json` (terms 1401-1450)
- `chunk_30.json` (terms 1451-1500)
- `chunk_31.json` (terms 1501-1550)
- `chunk_32.json` (terms 1551-1600)
- `chunk_33.json` (terms 1601-1603)

## Translation workflow:
1. Translate each chunk file using your preferred tool
2. Save completed translations as `chunk_XX_completed.json`
3. Run `python chunk_translations.py --merge` to combine all chunks
4. Run `python apply_bulk_translations.py` to apply to source files

## Sample prompt for external tools:
```
Please translate these Pali Buddhist terms to English and Sinhala.
Fill in the 'english' and 'sinhala' fields in the JSON.
Context: These are canonical Buddhist terms from Pali texts.
- Terms ending in 'suttaṃ' are discourse titles
- Terms ending in 'vaggo' are chapter names
- Use the 'sample_context' to understand usage
```
