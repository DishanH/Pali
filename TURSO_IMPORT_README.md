# Turso Database Import Guide

This guide explains how to import your Pali Tipitaka JSON data into a Turso database.

## 📋 Database Schema

The database has 4 main tables:

### 1. **nikayas** - Main collections
- `id`: Unique identifier (e.g., "anguttara", "digha")
- `name_pali`, `name_english`, `name_sinhala`: Names in different languages

### 2. **books** - Sub-collections within each Nikaya
- `id`: Unique identifier
- `nikaya_id`: Foreign key to nikayas
- `name`: Book name
- `title_pali`, `title_english`, `title_sinhala`: Titles
- `footer_pali`, `footer_english`, `footer_sinhala`: Footer text
- `description_english`, `description_sinhala`: Descriptions
- `total_chapters`: Number of chapters
- `version`, `last_updated`: Metadata

### 3. **chapters** - Individual chapters/samyuttas
- `id`: Unique identifier (e.g., "sn.5.1", "dn1")
- `book_id`: Foreign key to books
- `chapter_number`: Sequential number
- `title_pali`, `title_english`, `title_sinhala`: Chapter titles
- `description_english`, `description_sinhala`: Descriptions
- `link`: Path to chapter JSON file

### 4. **sections** - Individual suttas/sections
- `id`: Auto-increment primary key
- `chapter_id`: Foreign key to chapters
- `section_number`: Section number within chapter
- `pali`, `english`, `sinhala`: Full text content
- `pali_title`, `english_title`, `sinhala_title`: Section titles
- `vagga`, `vagga_english`, `vagga_sinhala`: Vagga (sub-section) information

### Full-Text Search
- `sections_fts`: Virtual FTS5 table for fast text search across all sections

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install libsql-experimental
```

Or install from requirements:
```bash
pip install -r turso_requirements.txt
```

### 2. Set Up Turso Database

If you don't have a Turso database yet:

```bash
# Install Turso CLI
# Windows (PowerShell):
irm get.turso.tech/install.ps1 | iex

# Create a new database
turso db create pali-tipitaka

# Get your database URL
turso db show pali-tipitaka --url

# Create an auth token
turso db tokens create pali-tipitaka
```

### 3. Configure Environment Variables

Set your Turso credentials:

**Windows (CMD):**
```cmd
set TURSO_DB_URL=libsql://your-database.turso.io
set TURSO_AUTH_TOKEN=your_auth_token_here
```

**Windows (PowerShell):**
```powershell
$env:TURSO_DB_URL="libsql://your-database.turso.io"
$env:TURSO_AUTH_TOKEN="your_auth_token_here"
```

**Linux/Mac:**
```bash
export TURSO_DB_URL="libsql://your-database.turso.io"
export TURSO_AUTH_TOKEN="your_auth_token_here"
```

### 4. Run the Import Script

```bash
python import_to_turso.py
```

## 📖 Import Options

The script provides an interactive menu:

### Option 1: Import Single Book Folder
- Import one book at a time (e.g., just "Mahāvaggo" from Saṃyuttanikāyo)
- Best for testing or incremental imports
- Example: Import only `Saṃyuttanikāyo/Mahāvaggo`

### Option 2: Import Entire Nikaya
- Import all books within a Nikaya
- Example: Import all of Saṃyuttanikāyo (all vaggas)

### Option 3: Import All Nikayas
- Import everything at once
- This will take some time depending on data size

### Option 4: Show Database Statistics
- View counts of nikayas, books, chapters, and sections
- Useful to verify import progress

## 📁 Folder Structure Expected

```
Aṅguttaranikāyo/
├── Ekakanipātapāḷi/
│   ├── book.json
│   └── chapters/
│       ├── an1.1-Rūpādivaggo.json
│       └── ...
├── Dukanipātapāḷi/
│   └── ...
└── pdfs/ (ignored)

Dīghanikāyo/
├── Sīlakkhandhavaggapāḷi/
│   ├── book.json
│   └── chapters/
│       ├── dn1-Brahmajālasuttaṃ.json
│       └── ...
└── ...

Majjhimanikāye/
└── ...

Saṃyuttanikāyo/
├── Mahāvaggo/
│   ├── book.json
│   └── chapters/
│       ├── sn.5.1-Maggasaṃyuttaṃ.json
│       └── ...
└── ...
```

## 🔍 Example Queries

After importing, you can query your data:

### Get all Nikayas
```sql
SELECT * FROM nikayas;
```

### Get all books in a Nikaya
```sql
SELECT * FROM books WHERE nikaya_id = 'samyutta';
```

### Get all chapters in a book
```sql
SELECT * FROM chapters WHERE book_id = 'Mahāvaggo';
```

### Get all sections in a chapter
```sql
SELECT * FROM sections WHERE chapter_id = 'sn.5.1' ORDER BY section_number;
```

### Full-text search in Pali
```sql
SELECT s.*, c.title_pali as chapter_title
FROM sections_fts 
JOIN sections s ON sections_fts.rowid = s.id
JOIN chapters c ON s.chapter_id = c.id
WHERE sections_fts MATCH 'bhagavā'
LIMIT 10;
```

### Search in English translations
```sql
SELECT s.*, c.title_english as chapter_title
FROM sections_fts 
JOIN sections s ON sections_fts.rowid = s.id
JOIN chapters c ON s.chapter_id = c.id
WHERE sections_fts.english MATCH 'meditation'
LIMIT 10;
```

### Get sections with vagga information
```sql
SELECT 
    chapter_id,
    section_number,
    vagga,
    vagga_english,
    pali_title,
    english_title
FROM sections 
WHERE vagga != '' 
ORDER BY chapter_id, section_number;
```

## 🎯 Import Strategy Recommendations

### For Testing
1. Start with **Option 1** - Import a single small book
2. Verify the data looks correct
3. Check statistics with **Option 4**

### For Production
1. Import one Nikaya at a time using **Option 2**
2. This allows you to:
   - Monitor progress
   - Handle errors per Nikaya
   - Verify data incrementally

### For Complete Import
- Use **Option 3** only after testing with smaller imports
- Ensure stable internet connection
- Monitor for any errors

## ⚠️ Important Notes

1. **PDF folders are automatically skipped** - The script ignores any folder named "pdfs"

2. **Duplicate handling** - The script uses `INSERT OR REPLACE`, so re-running imports will update existing data

3. **Transaction handling** - Each book import is committed separately, so partial imports are preserved

4. **Error handling** - If one book fails, the script continues with the next one

5. **Character encoding** - All files are read with UTF-8 encoding to support Pali and Sinhala characters

## 🐛 Troubleshooting

### Connection Error
```
Error: TURSO_DB_URL and TURSO_AUTH_TOKEN must be set
```
**Solution**: Set environment variables as shown in step 3

### File Not Found
```
❌ book.json not found in [path]
```
**Solution**: Ensure the folder structure matches the expected format

### Import Fails Midway
- Check database statistics to see what was imported
- Re-run the import for failed books (duplicates will be updated)

### Slow Import
- This is normal for large datasets
- Import one book at a time to monitor progress
- Consider importing during off-peak hours

## 📊 Performance Tips

1. **Batch imports**: Import one Nikaya at a time rather than individual books
2. **Network**: Ensure stable internet connection to Turso
3. **Monitoring**: Use Option 4 regularly to check progress
4. **Indexes**: The schema includes indexes for better query performance

## 🔐 Security

- Never commit your `.env` file or auth tokens to version control
- Rotate auth tokens periodically
- Use read-only tokens for client applications
- Keep write tokens secure for import operations

## 📝 Schema File

The `turso_schema.sql` file contains:
- Table definitions
- Indexes for performance
- FTS5 virtual table for full-text search
- Triggers to keep FTS index synchronized

You can also apply this schema manually using Turso CLI:
```bash
turso db shell pali-tipitaka < turso_schema.sql
```

## 🎉 Success Indicators

After successful import, you should see:
- ✓ Connected to Turso database
- ✓ Schema initialized
- ✓ Book metadata inserted
- ✓ Chapter metadata entries inserted
- ✓ Chapter files processed
- ✓ Sections inserted
- ✅ Successfully imported [book name]

Check final statistics to verify all data is imported!
