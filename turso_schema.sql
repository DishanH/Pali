-- Turso Database Schema for Pali Tipitaka
-- Updated schema to support the new standardized book.json structure
-- This schema supports the hierarchical structure: Basket > Collection > Book/Vagga/Nipata/Pannasa > Chapter > Section

-- Table: baskets (Pitaka level - Sutta, Vinaya, Abhidhamma)
CREATE TABLE IF NOT EXISTS baskets (
    id TEXT PRIMARY KEY,
    name_pali TEXT NOT NULL,
    name_english TEXT,
    name_sinhala TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: collections (Nikaya level - Digha, Majjhima, Samyutta, Anguttara)
CREATE TABLE IF NOT EXISTS collections (
    id TEXT PRIMARY KEY,
    basket_id TEXT NOT NULL,
    name_pali TEXT NOT NULL,
    name_english TEXT,
    name_sinhala TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (basket_id) REFERENCES baskets(id)
);

-- Table: books (Sub-collections/Vaggas/Nipatas/Pannasas within each Collection)
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    collection_id TEXT NOT NULL,
    book_type TEXT NOT NULL, -- 'vagga', 'nipata', 'pannasa'
    book_number INTEGER,
    book_id_pali TEXT, -- The original id from JSON (e.g., 'mahavagga', 'ekakanipata')
    name_pali TEXT NOT NULL,
    name_english TEXT,
    name_sinhala TEXT,
    title_pali TEXT NOT NULL,
    title_english TEXT,
    title_sinhala TEXT,
    footer_pali TEXT,
    footer_english TEXT,
    footer_sinhala TEXT,
    description_english TEXT,
    description_sinhala TEXT,
    total_chapters INTEGER,
    language_source TEXT,
    language_translations TEXT, -- JSON array as text
    version TEXT,
    last_updated TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES collections(id)
);

-- Table: chapters (Individual chapters/samyuttas within books)
CREATE TABLE IF NOT EXISTS chapters (
    id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL,
    chapter_number INTEGER,
    title_pali TEXT NOT NULL,
    title_english TEXT,
    title_sinhala TEXT,
    description_english TEXT,
    description_sinhala TEXT,
    link TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- Table: sections (Individual suttas/sections within chapters)
CREATE TABLE IF NOT EXISTS sections (
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

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_collections_basket ON collections(basket_id);
CREATE INDEX IF NOT EXISTS idx_books_collection ON books(collection_id);
CREATE INDEX IF NOT EXISTS idx_books_type ON books(book_type);
CREATE INDEX IF NOT EXISTS idx_chapters_book ON chapters(book_id);
CREATE INDEX IF NOT EXISTS idx_sections_chapter ON sections(chapter_id);
CREATE INDEX IF NOT EXISTS idx_sections_number ON sections(chapter_id, section_number);

-- Full-text search indexes for content search
CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
    chapter_id,
    section_number,
    pali,
    english,
    sinhala,
    pali_title,
    english_title,
    sinhala_title,
    vagga,
    vagga_english,
    vagga_sinhala,
    content=sections,
    content_rowid=id
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, chapter_id, section_number, pali, english, sinhala, pali_title, english_title, sinhala_title, vagga, vagga_english, vagga_sinhala)
    VALUES (new.id, new.chapter_id, new.section_number, new.pali, new.english, new.sinhala, new.pali_title, new.english_title, new.sinhala_title, new.vagga, new.vagga_english, new.vagga_sinhala);
END;

CREATE TRIGGER IF NOT EXISTS sections_ad AFTER DELETE ON sections BEGIN
    DELETE FROM sections_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS sections_au AFTER UPDATE ON sections BEGIN
    UPDATE sections_fts SET 
        chapter_id = new.chapter_id,
        section_number = new.section_number,
        pali = new.pali,
        english = new.english,
        sinhala = new.sinhala,
        pali_title = new.pali_title,
        english_title = new.english_title,
        sinhala_title = new.sinhala_title,
        vagga = new.vagga,
        vagga_english = new.vagga_english,
        vagga_sinhala = new.vagga_sinhala
    WHERE rowid = new.id;
END;

-- Insert initial basket data
INSERT OR IGNORE INTO baskets (id, name_pali, name_english, name_sinhala) VALUES 
('sutta', 'Suttapiṭaka', 'Basket of Discourses', 'සූත්‍ර පිටකය');

-- Insert initial collection data
INSERT OR IGNORE INTO collections (id, basket_id, name_pali, name_english, name_sinhala) VALUES 
('dighanikaya', 'sutta', 'Dīgha Nikāya', 'Long Discourses', 'දීඝ නිකාය'),
('majjhimanikaya', 'sutta', 'Majjhima Nikāya', 'Middle Length Discourses', 'මජ්ඣිම නිකාය'),
('samyuttanikaya', 'sutta', 'Saṃyutta Nikāya', 'Connected Discourses', 'සංයුත්ත නිකාය'),
('anguttaranikaya', 'sutta', 'Aṅguttara Nikāya', 'Numerical Discourses', 'අංගුත්තර නිකාය');
