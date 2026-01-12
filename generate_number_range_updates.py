#!/usr/bin/env python3
"""
Script to generate SQL UPDATE statements for numberRange field.
This script scans JSON files and generates SQL statements that can be executed.
"""

import os
import json
from pathlib import Path

def find_json_files():
    """Find all chapter JSON files in the directory structure."""
    json_files = []
    base_dirs = [
        "Aṅguttaranikāyo",
        "Dīghanikāyo",
        "Majjhimanikāye",
        "Saṃyuttanikāyo"
    ]
    
    for base_dir in base_dirs:
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.json') and 'chapters' in root:
                        json_files.append(os.path.join(root, file))
    
    return json_files

def generate_update_statements():
    """Generate SQL UPDATE statements for sections with numberRange."""
    json_files = find_json_files()
    
    updates = []
    total_with_range = 0
    
    print(f"-- SQL UPDATE statements for numberRange field")
    print(f"-- Generated from {len(json_files)} JSON files\n")
    print("BEGIN TRANSACTION;\n")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chapter_id = data.get('id')
            if not chapter_id:
                continue
            
            sections = data.get('sections', [])
            
            for section in sections:
                section_number = section.get('number')
                number_range = section.get('numberRange')
                
                if number_range:
                    total_with_range += 1
                    # Escape single quotes in SQL
                    number_range_escaped = number_range.replace("'", "''")
                    chapter_id_escaped = chapter_id.replace("'", "''")
                    
                    sql = f"UPDATE sections SET number_range = '{number_range_escaped}' WHERE chapter_id = '{chapter_id_escaped}' AND section_number = {section_number};"
                    print(sql)
                    updates.append({
                        'chapter_id': chapter_id,
                        'section_number': section_number,
                        'number_range': number_range
                    })
            
        except Exception as e:
            print(f"-- Error processing {json_file}: {e}")
            continue
    
    print("\nCOMMIT;")
    print(f"\n-- Total sections with numberRange: {total_with_range}")
    
    # Also save to a file
    with open('number_range_updates.sql', 'w', encoding='utf-8') as f:
        f.write(f"-- SQL UPDATE statements for numberRange field\n")
        f.write(f"-- Generated from {len(json_files)} JSON files\n\n")
        f.write("BEGIN TRANSACTION;\n\n")
        
        for update in updates:
            number_range_escaped = update['number_range'].replace("'", "''")
            chapter_id_escaped = update['chapter_id'].replace("'", "''")
            sql = f"UPDATE sections SET number_range = '{number_range_escaped}' WHERE chapter_id = '{chapter_id_escaped}' AND section_number = {update['section_number']};\n"
            f.write(sql)
        
        f.write("\nCOMMIT;\n")
        f.write(f"\n-- Total sections with numberRange: {total_with_range}\n")
    
    print(f"\n✓ SQL statements saved to: number_range_updates.sql")
    
    # Generate a summary report
    with open('number_range_summary.txt', 'w', encoding='utf-8') as f:
        f.write("NumberRange Field Summary\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total JSON files scanned: {len(json_files)}\n")
        f.write(f"Total sections with numberRange: {total_with_range}\n\n")
        f.write("Sections by chapter:\n")
        f.write("-"*60 + "\n")
        
        by_chapter = {}
        for update in updates:
            chapter = update['chapter_id']
            if chapter not in by_chapter:
                by_chapter[chapter] = []
            by_chapter[chapter].append(update)
        
        for chapter in sorted(by_chapter.keys()):
            f.write(f"\n{chapter}:\n")
            for update in by_chapter[chapter]:
                f.write(f"  Section {update['section_number']}: {update['number_range']}\n")
    
    print(f"✓ Summary report saved to: number_range_summary.txt")
    
    return total_with_range

def main():
    """Main execution function."""
    print("="*60)
    print("Generating SQL UPDATE statements for numberRange")
    print("="*60)
    print()
    
    try:
        total = generate_update_statements()
        
        print("\n" + "="*60)
        print("Next steps:")
        print("="*60)
        print("1. Run the migration: add_number_range_migration.sql")
        print("   This adds the number_range column to the sections table")
        print()
        print("2. Run the updates: number_range_updates.sql")
        print("   This populates the number_range field for relevant sections")
        print()
        print("You can execute these using:")
        print("  - Turso CLI: turso db shell <db-name> < file.sql")
        print("  - Or copy/paste into your database client")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
