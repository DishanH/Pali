# NumberRange Database Migration

## 🎯 Quick Summary

This migration adds a `number_range` column to your `sections` table to track condensed suttas. For example, section 102 might represent suttas 102-109.

**Impact**: 180 sections across 50+ chapters will be updated.

## 🚀 Quick Start (Choose One Method)

### Method 1: Windows Batch Script (Easiest)
```bash
run_number_range_migration.bat
```

### Method 2: Python Script
```bash
pip install libsql-experimental python-dotenv
python execute_number_range_migration.py
```

### Method 3: Turso CLI
```bash
turso db shell <your-db-name> < add_number_range_migration.sql
turso db shell <your-db-name> < number_range_updates.sql
```

## ✅ Verify It Worked

```sql
SELECT COUNT(*) FROM sections WHERE number_range IS NOT NULL;
-- Expected result: 180
```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| **Migration Files** | |
| `add_number_range_migration.sql` | Adds column & index |
| `number_range_updates.sql` | 180 UPDATE statements |
| `execute_number_range_migration.py` | Automated Python script |
| `run_number_range_migration.bat` | Windows batch script |
| **Documentation** | |
| `NUMBER_RANGE_QUICK_START.md` | ⭐ Start here |
| `NUMBER_RANGE_MIGRATION_GUIDE.md` | Detailed guide |
| `NUMBER_RANGE_IMPLEMENTATION_SUMMARY.md` | Technical details |
| `number_range_summary.txt` | Data report |
| **Utilities** | |
| `generate_number_range_updates.py` | Regenerate SQL if needed |
| `add_number_range_column.py` | Alternative approach |

## 📊 What Gets Updated

- **Aṅguttara Nikāya**: 83 sections
- **Saṃyutta Nikāya**: 97 sections
- **Total**: 180 sections

### Example Ranges
- `an1.10` section 102 → covers suttas 102-109
- `an5.29` section 308 → covers suttas 308-1151 (844 suttas!)
- `an7.10` section 96 → covers suttas 96-622 (527 suttas!)

## 🔍 Example Queries After Migration

```sql
-- Find all condensed sections
SELECT chapter_id, section_number, number_range
FROM sections
WHERE number_range IS NOT NULL;

-- Find which section contains sutta 150
SELECT chapter_id, section_number, number_range
FROM sections
WHERE number_range LIKE '%150%';

-- Count condensed sections per chapter
SELECT chapter_id, COUNT(*) as count
FROM sections
WHERE number_range IS NOT NULL
GROUP BY chapter_id
ORDER BY count DESC;
```

## 🛠️ Troubleshooting

### "libsql-experimental not found"
→ Use Method 3 (Turso CLI) or install: `pip install libsql-experimental`

### "duplicate column name"
→ Column already exists, skip to running `number_range_updates.sql`

### "0 rows updated"
→ Check if sections exist: `SELECT COUNT(*) FROM sections;`

## 📚 Need More Info?

1. **Quick Start**: `NUMBER_RANGE_QUICK_START.md`
2. **Full Guide**: `NUMBER_RANGE_MIGRATION_GUIDE.md`
3. **Technical Details**: `NUMBER_RANGE_IMPLEMENTATION_SUMMARY.md`
4. **Data Report**: `number_range_summary.txt`

## ⚠️ Important Notes

- ✅ Safe to run multiple times
- ✅ No data loss
- ✅ Backward compatible (nullable field)
- ✅ Transaction-wrapped for safety
- ✅ Includes rollback instructions

## 🎉 After Migration

Update your application to:
1. Display number ranges in the UI
2. Add API endpoints for range queries
3. Enable search by sutta number
4. Show "condensed section" indicators

---

**Status**: Ready to deploy
**Last Updated**: January 12, 2026
**Files Generated**: 13 files (scripts, SQL, docs)
