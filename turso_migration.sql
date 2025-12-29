-- Migration script to update existing Turso database to support new book.json structure
-- Run this script if you have an existing database with the old schema

-- Step 1: Create new tables for the updated structure
CREATE TABLE IF NOT EXISTS baskets (
    id TEXT PRIMARY KEY,
    name_pali TEXT NOT NULL,
    name_english TEXT,
    name_sinhala TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS collections (
    id TEXT PRIMARY KEY,
    basket_id TEXT NOT NULL,
    name_pali TEXT NOT NULL,
    name_english TEXT,
    name_sinhala TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (basket_id) REFERENCES baskets(id)
);

-- Step 2: Add new columns to existing books table
ALTER TABLE books ADD COLUMN collection_id TEXT;
ALTER TABLE books ADD COLUMN book_type TEXT;
ALTER TABLE books ADD COLUMN book_number INTEGER;
ALTER TABLE books ADD COLUMN book_id_pali TEXT;
ALTER TABLE books ADD COLUMN name_pali TEXT;
ALTER TABLE books ADD COLUMN name_english TEXT;
ALTER TABLE books ADD COLUMN name_sinhala TEXT;
ALTER TABLE books ADD COLUMN language_source TEXT;
ALTER TABLE books ADD COLUMN language_translations TEXT;

-- Step 3: Insert initial data
INSERT OR IGNORE INTO baskets (id, name_pali, name_english, name_sinhala) VALUES 
('sutta', 'Suttapiṭaka', 'Basket of Discourses', 'සූත්‍ර පිටකය');

INSERT OR IGNORE INTO collections (id, basket_id, name_pali, name_english, name_sinhala) VALUES 
('dighanikaya', 'sutta', 'Dīgha Nikāya', 'Long Discourses', 'දීඝ නිකාය'),
('majjhimanikaya', 'sutta', 'Majjhima Nikāya', 'Middle Length Discourses', 'මජ්ඣිම නිකාය'),
('samyuttanikaya', 'sutta', 'Saṃyutta Nikāya', 'Connected Discourses', 'සංයුත්ත නිකාය'),
('anguttaranikaya', 'sutta', 'Aṅguttara Nikāya', 'Numerical Discourses', 'අංගුත්තර නිකාය');

-- Step 4: Migrate existing data (if any)
-- Update books table to use collection_id instead of nikaya_id
UPDATE books SET collection_id = nikaya_id WHERE nikaya_id IS NOT NULL;

-- Step 5: Create new indexes
CREATE INDEX IF NOT EXISTS idx_collections_basket ON collections(basket_id);
CREATE INDEX IF NOT EXISTS idx_books_collection ON books(collection_id);
CREATE INDEX IF NOT EXISTS idx_books_type ON books(book_type);

-- Step 6: Drop old columns and tables (optional - uncomment if you want to clean up)
-- Note: SQLite doesn't support DROP COLUMN directly, so you'd need to recreate the table
-- ALTER TABLE books DROP COLUMN nikaya_id; -- Not supported in SQLite
-- DROP TABLE IF EXISTS nikayas; -- Only if you're sure you don't need it

-- Step 7: Update any existing foreign key references
-- This would depend on your specific data and requirements