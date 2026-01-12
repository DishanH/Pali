# NumberRange Migration - Quick Start

## What This Does

Adds a `number_range` column to the `sections` table to track condensed suttas (e.g., section 102 covers suttas 102-109).

## Quick Stats

- **180 sections** across **50+ chapters** need the numberRange field
- Affects Aṅguttara and Saṃyutta Nikāyas
- No data loss - only adds a new optional field

## Run the Migration (Choose One)

### Option A: Automatic (Windows)
```bash
run_number_range_migration.bat
```

### Option B: Python Script
```bash
pip install libsql-experimental python-dotenv
python execute_number_range_migration.py
```

### Option C: Manual SQL
```bash
# Using Turso CLI
turso db shell <your-db-name> < add_number_range_migration.sql
turso db shell <your-db-name> < number_range_updates.sql
```

## Verify It Worked

```sql
-- Should return 180
SELECT COUNT(*) FROM sections WHERE number_range IS NOT NULL;

-- View examples
SELECT chapter_id, section_number, number_range 
FROM sections 
WHERE number_range IS NOT NULL 
LIMIT 5;
```

## Files Created

| File | Purpose |
|------|---------|
| `add_number_range_migration.sql` | Adds the column |
| `number_range_updates.sql` | Populates the data (180 UPDATEs) |
| `execute_number_range_migration.py` | Automated Python script |
| `run_number_range_migration.bat` | Windows batch script |
| `number_range_summary.txt` | Detailed report |
| `NUMBER_RANGE_MIGRATION_GUIDE.md` | Full documentation |

## Example Usage After Migration

```sql
-- Find all condensed sections
SELECT * FROM sections WHERE number_range IS NOT NULL;

-- Search within a range
SELECT * FROM sections 
WHERE chapter_id = 'an1.10' 
  AND number_range LIKE '%102%';
```

## Need Help?

See `NUMBER_RANGE_MIGRATION_GUIDE.md` for detailed instructions and troubleshooting.
