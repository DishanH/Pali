# 🚀 Quick Start Guide - Turso Import

Get your Pali Tipitaka data into Turso in 5 minutes!

## ⚡ Super Quick Setup

### 1. Install Turso CLI (if you don't have it)

**Windows (PowerShell):**
```powershell
irm get.turso.tech/install.ps1 | iex
```

**Mac/Linux:**
```bash
curl -sSfL https://get.tur.so/install.sh | bash
```

### 2. Create Database

```bash
# Create database
turso db create pali-tipitaka

# Get database URL
turso db show pali-tipitaka --url

# Create auth token
turso db tokens create pali-tipitaka
```

### 3. Set Environment Variables

**Windows CMD:**
```cmd
set TURSO_DB_URL=libsql://pali-tipitaka-[your-username].turso.io
set TURSO_AUTH_TOKEN=eyJhbGc...your-token-here
```

**Windows PowerShell:**
```powershell
$env:TURSO_DB_URL="libsql://pali-tipitaka-[your-username].turso.io"
$env:TURSO_AUTH_TOKEN="eyJhbGc...your-token-here"
```

### 4. Install Python Dependencies

```bash
pip install libsql-experimental
```

### 5. Run Import

```bash
python import_to_turso.py
```

### 6. Choose Import Option

```
1. Import single book folder    ← Start here for testing
2. Import entire Nikaya         ← Recommended for production
3. Import all Nikayas           ← Use after testing
4. Show database statistics     ← Check progress
5. Exit
```

## 📖 Recommended Import Order

### For First Time (Testing)

1. **Test with one book:**
   - Choose Option 1
   - Select: Saṃyuttanikāyo → Mahāvaggo
   - Verify data looks correct

2. **Check statistics:**
   - Choose Option 4
   - Should show: 1 nikaya, 1 book, ~12 chapters, ~hundreds of sections

3. **Test queries:**
   ```bash
   python query_examples.py
   ```

### For Production Import

1. **Import one Nikaya at a time:**
   - Choose Option 2
   - Start with smallest: Dīghanikāyo
   - Check statistics after each
   - Continue with others

2. **Or import everything:**
   - Choose Option 3
   - Wait for completion
   - Check final statistics

## 🎯 What Gets Imported

```
Your Folder Structure:
Saṃyuttanikāyo/
  └── Mahāvaggo/
      ├── book.json              → books table
      └── chapters/
          ├── sn.5.1-*.json      → chapters + sections tables
          ├── sn.5.2-*.json
          └── ...

Becomes Database:
nikayas table:
  - samyutta | Saṃyutta Nikāya | Connected Discourses | ...

books table:
  - Mahāvaggo | samyutta | The Great Division | ...

chapters table:
  - sn.5.1 | Mahāvaggo | Maggasaṃyuttaṃ | ...
  - sn.5.2 | Mahāvaggo | Bojjhaṅgasaṃyuttaṃ | ...

sections table:
  - sn.5.1 | 1 | Evaṃ me sutaṃ... | Thus have I heard... | ...
  - sn.5.1 | 2 | ... | ... | ...
```

## 🔍 Quick Test Queries

After importing, test with these queries:

### Using Turso CLI:
```bash
turso db shell pali-tipitaka
```

Then run:
```sql
-- Count everything
SELECT COUNT(*) FROM sections;

-- Get first sutta
SELECT pali_title, english_title 
FROM sections 
WHERE chapter_id = 'sn.5.1' 
LIMIT 1;

-- Search for "bhagavā"
SELECT chapter_id, section_number, pali_title
FROM sections_fts 
WHERE pali MATCH 'bhagavā' 
LIMIT 5;
```

### Using Python:
```bash
python query_examples.py
```

## 📊 Expected Results

After importing **Saṃyuttanikāyo/Mahāvaggo**:
- ✓ 1 Nikaya (Saṃyuttanikāyo)
- ✓ 1 Book (Mahāvaggo)
- ✓ ~12 Chapters (sn.5.1 to sn.5.12)
- ✓ ~hundreds of Sections (individual suttas)

After importing **all 4 Nikayas**:
- ✓ 4 Nikayas
- ✓ 20-30 Books
- ✓ 200-300 Chapters
- ✓ 5,000-10,000+ Sections

## ⚠️ Common Issues

### Issue: "TURSO_DB_URL not set"
**Fix:** Set environment variables (see step 3)

### Issue: "Connection failed"
**Fix:** Check your database URL and token are correct
```bash
turso db show pali-tipitaka --url
turso db tokens create pali-tipitaka
```

### Issue: "book.json not found"
**Fix:** Make sure you're running from the project root directory where the Nikaya folders are

### Issue: Import is slow
**Fix:** This is normal! Each book can take 30-60 seconds depending on size

## 🎉 Success Checklist

After import, you should see:
- [x] ✓ Connected to Turso database
- [x] ✓ Schema initialized
- [x] ✓ Book metadata inserted
- [x] ✓ Chapter metadata entries inserted
- [x] ✓ Chapter files processed
- [x] ✓ Sections inserted
- [x] ✅ Successfully imported [book name]

## 📱 Next Steps

### 1. Verify Data
```bash
python query_examples.py
```

### 2. Build Your App
Use the database in your application:
- Web app (React, Vue, etc.)
- Mobile app (React Native, Flutter)
- Desktop app (Electron, Tauri)
- API server (Node.js, Python, Go)

### 3. Query Examples
See `query_examples.py` for:
- Browsing hierarchy
- Full-text search
- Getting complete suttas
- Statistics and analytics

### 4. Read Documentation
- `TURSO_IMPORT_README.md` - Full documentation
- `DATABASE_STRUCTURE.md` - Schema details
- `turso_schema.sql` - Raw SQL schema

## 🔗 Useful Links

- **Turso Docs:** https://docs.turso.tech/
- **libSQL Python:** https://github.com/libsql/libsql-client-py
- **Turso Dashboard:** https://turso.tech/app

## 💡 Pro Tips

1. **Start small:** Import one book first to test
2. **Check stats:** Use Option 4 frequently to monitor progress
3. **Backup:** Turso automatically backs up your data
4. **Scale:** Turso handles millions of rows easily
5. **Search:** Always use FTS5 for text search (it's fast!)

## 🆘 Need Help?

1. Check `TURSO_IMPORT_README.md` for detailed docs
2. Run `python query_examples.py` to see example queries
3. Check Turso docs: https://docs.turso.tech/
4. Verify your data structure matches expected format

## ✨ You're Ready!

Your Pali Tipitaka database is now:
- ✅ Stored in Turso (edge database)
- ✅ Searchable (full-text search)
- ✅ Multilingual (Pali, English, Sinhala)
- ✅ Accessible globally (Turso's edge network)
- ✅ Ready for your app!

Happy building! 🎊
