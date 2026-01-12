#!/usr/bin/env python3
"""
Script to batch update all fixed JSON files in Turso database
"""

import json
import os
import sys
from pathlib import Path

# Import database connection utilities
try:
    from config import get_turso_connection
except ImportError:
    print("Error: config.py not found. Please ensure database configuration is available.")
    sys.exit(1)

def update_chapter_in_database(file_path, conn):
    """
    Update a specific chapter file in the Turso database
    """
    try:
        # Load the JSON data
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        cursor = conn.cursor()
        
        chapter_id = chapter_data['id']
        print(f"Updating chapter {chapter_id}...")
        
        # Update the chapter title
        cursor.execute("""
            UPDATE chapters 
            SET title_pali = ?, title_english = ?, title_sinhala = ?
            WHERE id = ?
        """, (
            chapter_data['title']['pali'],
            chapter_data['title']['english'], 
            chapter_data['title']['sinhala'],
            chapter_id
        ))
        
        # Update sections
        sections_updated = 0
        for section in chapter_data['sections']:
            section_number = section['number']
            
            cursor.execute("""
                UPDATE sections 
                SET pali_text = ?, english_text = ?, sinhala_text = ?, pali_title = ?
                WHERE chapter_id = ? AND number = ?
            """, (
                section['pali'],
                section['english'],
                section['sinhala'],
                section.get('paliTitle', ''),
                chapter_id,
                section_number
            ))
            sections_updated += 1
        
        # Update footer if it exists
        if 'footer' in chapter_data:
            cursor.execute("""
                UPDATE chapters 
                SET footer_pali = ?, footer_english = ?, footer_sinhala = ?
                WHERE id = ?
            """, (
                chapter_data['footer']['pali'],
                chapter_data['footer']['english'],
                chapter_data['footer']['sinhala'],
                chapter_id
            ))
        
        cursor.close()
        print(f"  ✓ Updated {sections_updated} sections")
        return True
        
    except Exception as e:
        print(f"  ✗ Error updating {file_path}: {e}")
        return False

def main():
    """
    Main function to batch update files in database
    """
    # Get database connection
    try:
        conn = get_turso_connection()
        print("✓ Connected to Turso database")
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        return
    
    # Find all JSON files that might have been fixed
    json_files = []
    
    # Search in the Anguttara directory
    anguttara_path = Path("Aṅguttaranikāyo")
    if anguttara_path.exists():
        json_files.extend(anguttara_path.rglob("*.json"))
    
    # Also check other directories
    for directory in ["Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            json_files.extend(dir_path.rglob("*.json"))
    
    if not json_files:
        print("No JSON files found to update")
        conn.close()
        return
    
    print(f"Found {len(json_files)} JSON files to potentially update")
    
    # For now, let's just update the specific file we know was fixed
    specific_file = Path("Aṅguttaranikāyo/Dukanipātapāḷi/chapters/an2.2-Adhikaraṇavaggo.json")
    
    if specific_file.exists():
        print(f"\nUpdating the fixed file: {specific_file}")
        if update_chapter_in_database(specific_file, conn):
            # Commit the changes
            conn.commit()
            print("✓ Changes committed to database")
        else:
            print("✗ Failed to update file")
    else:
        print(f"✗ Fixed file not found: {specific_file}")
    
    # Close connection
    conn.close()
    print("\n✓ Database connection closed")

if __name__ == "__main__":
    main()