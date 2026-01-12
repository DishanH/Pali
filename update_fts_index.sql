-- Update script to rebuild sections_fts with vagga and title fields
-- Run this against your existing Turso database

-- Step 1: Drop existing FTS table and triggers
DROP TRIGGER IF EXISTS sections_au;
DROP TRIGGER IF EXISTS sections_ad;
DROP TRIGGER IF EXISTS sections_ai;
DROP TABLE IF EXISTS sections_fts;

-- Step 2: Recreate FTS table with all fields including vagga and titles
CREATE VIRTUAL TABLE sections_fts USING fts5(
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

-- Step 3: Populate FTS table with existing data
INSERT INTO sections_fts(rowid, chapter_id, section_number, pali, english, sinhala, pali_title, english_title, sinhala_title, vagga, vagga_english, vagga_sinhala)
SELECT id, chapter_id, section_number, pali, english, sinhala, pali_title, english_title, sinhala_title, vagga, vagga_english, vagga_sinhala
FROM sections;

-- Step 4: Recreate triggers to keep FTS in sync
CREATE TRIGGER sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, chapter_id, section_number, pali, english, sinhala, pali_title, english_title, sinhala_title, vagga, vagga_english, vagga_sinhala)
    VALUES (new.id, new.chapter_id, new.section_number, new.pali, new.english, new.sinhala, new.pali_title, new.english_title, new.sinhala_title, new.vagga, new.vagga_english, new.vagga_sinhala);
END;

CREATE TRIGGER sections_ad AFTER DELETE ON sections BEGIN
    DELETE FROM sections_fts WHERE rowid = old.id;
END;

CREATE TRIGGER sections_au AFTER UPDATE ON sections BEGIN
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
