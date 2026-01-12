# NumberRange Migration Guide

## Overview

This guide explains how to add the `numberRange` column to the `sections` table in your Turso database and populate it with data from the JSON files.

## What is numberRange?

The `numberRange` field is used in sections where multiple suttas are condensed into a single entry. For example:
- Section 102 might represent suttas 102-109
- Section 118 might represent suttas 118-128

This field helps track which sutta numbers are covered by a condensed section.

## Migration Summary

- **Total JSON files scanned**: 291
- **Total sections with numberRange**: 180
- **Affected chapters**: 50+ chapters across Aṅguttara and Saṃyutta Nikāyas

## Migration Files Generated

1. **add_number_range_migration.sql** - Adds the `number_range` column to the sections table
2. **number_range_updates.sql** - Contains 180 UPDATE statements to populate the field
3. **number_range_summary.txt** - Detailed report of all sections with numberRange
4. **execute_number_range_migration.py** - Python script to execute the migration automatically

## Option 1: Automatic Migration (Recommended)

If you have `libsql-experimental` installed:

```bash
# Install dependencies (if not already installed)
pip install libsql-experimental python-dotenv

# Run the migration script
python execute_number_range_migration.py
```

The script will:
1. Add the `number_range` column
2. Create an index for better performance
3. Update all 180 sections with their numberRange values
4. Verify the migration was successful

## Option 2: Manual Migration via Turso CLI

If you prefer to run SQL directly:

```bash
# Step 1: Add the column
turso db shell <your-db-name> < add_number_range_migration.sql

# Step 2: Update the data
turso db shell <your-db-name> < number_range_updates.sql
```

## Option 3: Manual Migration via Database Client

1. Connect to your Turso database using your preferred client
2. Run the contents of `add_number_range_migration.sql`:
   ```sql
   ALTER TABLE sections ADD COLUMN number_range TEXT;
   CREATE INDEX IF NOT EXISTS idx_sections_number_range ON sections(number_range);
   ```
3. Run the contents of `number_range_updates.sql` (180 UPDATE statements)

## Verification

After running the migration, verify it worked:

```sql
-- Check column exists
PRAGMA table_info(sections);

-- Count sections with number_range
SELECT COUNT(*) FROM sections WHERE number_range IS NOT NULL;
-- Expected: 180

-- View some examples
SELECT chapter_id, section_number, number_range 
FROM sections 
WHERE number_range IS NOT NULL
LIMIT 10;
```

## Example Queries Using numberRange

Once migrated, you can query sections by their range:

```sql
-- Find all condensed sections
SELECT chapter_id, section_number, number_range, pali_title
FROM sections
WHERE number_range IS NOT NULL
ORDER BY chapter_id, section_number;

-- Find sections covering a specific sutta number
SELECT chapter_id, section_number, number_range
FROM sections
WHERE number_range LIKE '%102%'
  AND chapter_id = 'an1.10';

-- Count condensed sections per chapter
SELECT chapter_id, COUNT(*) as condensed_count
FROM sections
WHERE number_range IS NOT NULL
GROUP BY chapter_id
ORDER BY condensed_count DESC;
```

## Schema Changes

### Before Migration
```sql
CREATE TABLE sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id TEXT NOT NULL,
    section_number INTEGER NOT NULL,
    pali TEXT NOT NULL,
    english TEXT,
    sinhala TEXT,
    pali_title TEXT,
    english_title TEXT,
    sinhala_title TEXT,
    vagga TEXT,
    vagga_english TEXT,
    vagga_sinhala TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);
```

### After Migration
```sql
CREATE TABLE sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id TEXT NOT NULL,
    section_number INTEGER NOT NULL,
    pali TEXT NOT NULL,
    english TEXT,
    sinhala TEXT,
    pali_title TEXT,
    english_title TEXT,
    sinhala_title TEXT,
    vagga TEXT,
    vagga_english TEXT,
    vagga_sinhala TEXT,
    number_range TEXT,  -- NEW COLUMN
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);

-- New index
CREATE INDEX idx_sections_number_range ON sections(number_range);
```

## Affected Collections

### Aṅguttara Nikāya
- Ekakanipāta (Book of Ones): 45 sections
- Dukanipāta (Book of Twos): 3 sections
- Tikanipāta (Book of Threes): 2 sections
- Pañcakanipāta (Book of Fives): 6 sections
- Chakkanipāta (Book of Sixes): 3 sections
- Sattakanipāta (Book of Sevens): 3 sections
- Navakanipāta (Book of Nines): 3 sections
- Dasakanipāta (Book of Tens): 5 sections
- Ekādasakanipāta (Book of Elevens): 13 sections

### Saṃyutta Nikāya
- Sagāthāvagga: 97 sections across multiple saṃyuttas

## Rollback

If you need to rollback the migration:

```sql
-- Remove the column (SQLite doesn't support DROP COLUMN directly)
-- You would need to recreate the table without the column
-- Or simply leave it as NULL values don't affect existing functionality

-- Remove the index
DROP INDEX IF EXISTS idx_sections_number_range;
```

## Troubleshooting

### Error: "duplicate column name"
The column already exists. Skip to step 2 (updating data).

### Error: "no such table: sections"
Make sure you're connected to the correct database and the schema has been initialized.

### Error: "libsql-experimental not found"
Use Option 2 or 3 (manual migration) instead.

### Updates show 0 rows affected
The sections might not exist in your database yet. Check if the data has been imported:
```sql
SELECT COUNT(*) FROM sections;
```

## Support

For issues or questions:
1. Check the `number_range_summary.txt` file for details on affected sections
2. Review the generated SQL in `number_range_updates.sql`
3. Verify your database connection settings in `.env`

## Next Steps

After migration, you may want to:
1. Update your application code to display numberRange information
2. Add API endpoints to query by number range
3. Update documentation to reflect the new field
4. Consider adding this field to your FTS index if needed for search
