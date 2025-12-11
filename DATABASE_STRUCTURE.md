# Turso Database Structure for Pali Tipitaka

## 📊 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE STRUCTURE                          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│    NIKAYAS       │  (Main Collections)
├──────────────────┤
│ id (PK)          │  e.g., "anguttara", "digha", "majjhima", "samyutta"
│ name_pali        │  e.g., "Aṅguttara Nikāya"
│ name_english     │  e.g., "Numerical Discourses"
│ name_sinhala     │  e.g., "අංගුත්තර නිකාය"
│ created_at       │
└────────┬─────────┘
         │
         │ 1:N
         │
┌────────▼─────────┐
│     BOOKS        │  (Sub-collections/Vaggas)
├──────────────────┤
│ id (PK)          │  e.g., "Mahāvaggo", "silakkhandhavagga"
│ nikaya_id (FK)   │  → nikayas.id
│ name             │  e.g., "Mahāvaggo"
│ title_pali       │
│ title_english    │
│ title_sinhala    │
│ footer_pali      │
│ footer_english   │
│ footer_sinhala   │
│ description_*    │
│ total_chapters   │
│ version          │
│ last_updated     │
│ created_at       │
└────────┬─────────┘
         │
         │ 1:N
         │
┌────────▼─────────┐
│    CHAPTERS      │  (Individual Samyuttas/Suttas)
├──────────────────┤
│ id (PK)          │  e.g., "sn.5.1", "dn1", "an1.1"
│ book_id (FK)     │  → books.id
│ chapter_number   │  Sequential number
│ title_pali       │  e.g., "Maggasaṃyuttaṃ"
│ title_english    │  e.g., "Connected Discourses on the Path"
│ title_sinhala    │  e.g., "මාර්ග සංයුත්තය"
│ description_*    │
│ link             │  Path to JSON file
│ created_at       │
└────────┬─────────┘
         │
         │ 1:N
         │
┌────────▼─────────┐
│    SECTIONS      │  (Individual Suttas/Teachings)
├──────────────────┤
│ id (PK)          │  Auto-increment
│ chapter_id (FK)  │  → chapters.id
│ section_number   │  Number within chapter
│ pali             │  Full Pali text
│ english          │  Full English translation
│ sinhala          │  Full Sinhala translation
│ pali_title       │  e.g., "Avijjāsuttaṃ"
│ english_title    │  e.g., "Ignorance Sutta"
│ sinhala_title    │  e.g., "අවිද්‍යා සූත්‍රය"
│ vagga            │  Sub-section (optional)
│ vagga_english    │  e.g., "Section on Ignorance"
│ vagga_sinhala    │  e.g., "අවිද්‍යා වර්ගය"
│ created_at       │
└──────────────────┘

┌──────────────────┐
│  SECTIONS_FTS    │  (Full-Text Search Virtual Table)
├──────────────────┤
│ rowid            │  → sections.id
│ chapter_id       │  Indexed for search
│ section_number   │  Indexed for search
│ pali             │  Full-text indexed
│ english          │  Full-text indexed
│ sinhala          │  Full-text indexed
└──────────────────┘
```

## 🗂️ Data Hierarchy

```
Nikaya (Collection)
  └── Book/Vagga (Sub-collection)
      └── Chapter (Samyutta/Group)
          └── Section (Individual Sutta)
              ├── Pali Text
              ├── English Translation
              ├── Sinhala Translation
              └── Optional: Vagga (Sub-section)
```

## 📝 Example Data Flow

### Example 1: Saṃyuttanikāyo Structure

```
Nikaya: Saṃyuttanikāyo (samyutta)
  │
  ├── Book: Mahāvaggo
  │     │
  │     ├── Chapter: sn.5.1 - Maggasaṃyuttaṃ
  │     │     │
  │     │     ├── Section 1: Avijjāsuttaṃ
  │     │     │   ├── Vagga: Avijjāvaggo
  │     │     │   ├── Pali: "Evaṃ me sutaṃ..."
  │     │     │   ├── English: "Thus have I heard..."
  │     │     │   └── Sinhala: "මා විසින් මෙසේ අසන ලදි..."
  │     │     │
  │     │     ├── Section 2: Upaḍḍhasuttaṃ
  │     │     └── Section 3: Sāriputtasuttaṃ
  │     │
  │     ├── Chapter: sn.5.2 - Bojjhaṅgasaṃyuttaṃ
  │     └── Chapter: sn.5.3 - Satipaṭṭhānasaṃyuttaṃ
  │
  └── Book: Nidānavaggo
        └── ...
```

### Example 2: Dīghanikāyo Structure

```
Nikaya: Dīghanikāyo (digha)
  │
  └── Book: Sīlakkhandhavaggapāḷi
        │
        ├── Chapter: dn1 - Brahmajālasuttaṃ
        │     │
        │     └── Section 1: (Full sutta text)
        │           ├── Pali: "Evaṃ me sutaṃ..."
        │           ├── English: "Thus have I heard..."
        │           └── Sinhala: "මා විසින් මෙසේ අසන ලදි..."
        │
        ├── Chapter: dn2 - Sāmaññaphalasuttaṃ
        └── Chapter: dn3 - Ambaṭṭhasuttaṃ
```

## 🔍 Key Features

### 1. Hierarchical Structure
- 4 levels: Nikaya → Book → Chapter → Section
- Foreign key relationships maintain data integrity
- Easy navigation through the hierarchy

### 2. Multilingual Support
- All text fields available in 3 languages:
  - Pali (original)
  - English (translation)
  - Sinhala (translation)

### 3. Flexible Vagga Support
- Some sections have vagga (sub-sections)
- Vagga fields are optional (can be empty)
- Vagga information includes all 3 languages

### 4. Full-Text Search
- FTS5 virtual table for fast searching
- Search across all languages
- Automatically synchronized with main table

### 5. Metadata
- Timestamps for all records
- Version tracking for books
- Links to original JSON files
- Descriptions and summaries

## 📊 Table Sizes (Estimated)

Based on typical Tipitaka structure:

| Table    | Estimated Rows | Description                    |
|----------|----------------|--------------------------------|
| nikayas  | 4              | 4 main Nikayas                |
| books    | 20-30          | Sub-collections per Nikaya    |
| chapters | 200-300        | Individual chapters/samyuttas |
| sections | 5,000-10,000+  | Individual suttas/teachings   |

## 🎯 Query Patterns

### Common Queries

1. **Browse by hierarchy**
   ```sql
   SELECT * FROM nikayas
   → SELECT * FROM books WHERE nikaya_id = ?
   → SELECT * FROM chapters WHERE book_id = ?
   → SELECT * FROM sections WHERE chapter_id = ?
   ```

2. **Search text**
   ```sql
   SELECT * FROM sections_fts WHERE pali MATCH 'search_term'
   ```

3. **Get complete sutta**
   ```sql
   SELECT * FROM sections 
   WHERE chapter_id = ? AND section_number = ?
   ```

4. **Find by vagga**
   ```sql
   SELECT * FROM sections 
   WHERE vagga = 'Avijjāvaggo'
   ```

## 🔐 Indexes

The schema includes indexes on:
- `books.nikaya_id` - Fast book lookup by nikaya
- `chapters.book_id` - Fast chapter lookup by book
- `sections.chapter_id` - Fast section lookup by chapter
- `sections.(chapter_id, section_number)` - Fast specific section lookup
- FTS5 indexes on all text fields for full-text search

## 💾 Storage Considerations

### Text Fields
- `pali`, `english`, `sinhala` in sections table can be large
- Each section can contain full sutta text (100s to 1000s of characters)
- FTS5 index adds ~30-50% storage overhead

### Optimization Tips
1. Use FTS5 for search, not LIKE queries
2. Index foreign keys for joins
3. Consider pagination for large result sets
4. Cache frequently accessed chapters

## 🚀 Performance

### Fast Operations
- Browsing hierarchy (indexed foreign keys)
- Full-text search (FTS5)
- Specific section lookup (composite index)

### Slower Operations
- Searching without FTS (LIKE queries)
- Aggregations across all sections
- Complex multi-language searches

### Recommendations
- Always use FTS5 for text search
- Limit result sets with LIMIT clause
- Use prepared statements for repeated queries
- Consider caching at application level
