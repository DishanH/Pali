-- Turso Database Schema for Pali Tipitaka
-- This schema supports the hierarchical structure: Nikaya > Book/Vagga > Chapter > Section

-- Table: nikayas (Main collections)
CREATE TABLE IF NOT EXISTS nikayas (
    id TEXT PRIMARY KEY,
    name_pali TEXT NOT NULL,
    name_english TEXT,
    name_sinhala TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: books (Sub-collections/Vaggas within each Nikaya)
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    nikaya_id TEXT NOT NULL,
    name TEXT NOT NULL,
    title_pali TEXT NOT NULL,
    title_english TEXT,
    title_sinhala TEXT,
    footer_pali TEXT,
    footer_english TEXT,
    footer_sinhala TEXT,
    description_english TEXT,
    description_sinhala TEXT,
    total_chapters INTEGER,
    version TEXT,
    last_updated TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nikaya_id) REFERENCES nikayas(id)
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
CREATE INDEX IF NOT EXISTS idx_books_nikaya ON books(nikaya_id);
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
    content=sections,
    content_rowid=id
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, chapter_id, section_number, pali, english, sinhala)
    VALUES (new.id, new.chapter_id, new.section_number, new.pali, new.english, new.sinhala);
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
        sinhala = new.sinhala
    WHERE rowid = new.id;
END;
