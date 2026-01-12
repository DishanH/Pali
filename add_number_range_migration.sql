-- Migration script to add numberRange column to sections table
-- Run this script using Turso CLI or your database client

-- Step 1: Add the number_range column to sections table
ALTER TABLE sections ADD COLUMN number_range TEXT;

-- Step 2: Create an index for better query performance (optional)
CREATE INDEX IF NOT EXISTS idx_sections_number_range ON sections(number_range);

-- Verify the column was added
-- PRAGMA table_info(sections);
