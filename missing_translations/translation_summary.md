# Missing Translations Summary

## Statistics
- **Books scanned**: 22
- **Chapters scanned**: 291
- **Sections scanned**: 6576
- **Missing English translations**: 1603
- **Missing Sinhala translations**: 1603

## Translation Strategy
Given Google Translate's free quota of 20 requests per day:

1. **Prioritized by frequency**: Most commonly used terms first
2. **Batch files created**: 20-item batches for daily translation
3. **Context provided**: Shows where each term is used
4. **Multiple formats**: CSV for manual editing, JSON for automation

## Files Generated
- `missing_english_batch_20.txt`: Daily batch of 20 English terms for Google Translate
- `missing_english_translations.csv`: CSV file for manual English translation editing
- `missing_english_translations.json`: JSON file with English translation data
- `missing_sinhala_batch_20.txt`: Daily batch of 20 Sinhala terms for Google Translate
- `missing_sinhala_translations.csv`: CSV file for manual Sinhala translation editing
- `missing_sinhala_translations.json`: JSON file with Sinhala translation data
- `translation_summary.md`: This summary report

## Usage Instructions
1. Start with `missing_english_batch_20.txt` or `missing_sinhala_batch_20.txt`
2. Translate 20 items per day using Google Translate
3. Update the CSV files with translations
4. Use the update script (to be created) to apply translations back to source files
