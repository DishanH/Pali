#!/usr/bin/env python3
"""
Script to update the fixed JSON file in Turso database
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

def update_chapter_in_database(file_path):
    """
    Update a specific chapter file in the Turso database
    """
    try:
        # Load the fixed JSON data
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        # Get database connection
        conn = get_turso_connection()
        cursor = conn.cursor()
        
        chapter_id = chapter_data['id']
        print(f"Updating chapter {chapter_id} in database...")
        
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
            
            print(f"  ✓ Updated section {section_number}")
        
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
            print(f"  ✓ Updated footer")
        
        # Commit changes
        conn.commit()
        print(f"✓ Successfully updated chapter {chapter_id} in database")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error updating database for {file_path}: {e}")
        return False

def main():
    """
    Main function to update the fixed file in database
    """
    # The specific file we fixed
    file_path = Path("Aṅguttaranikāyo/Dukanipātapāḷi/chapters/an2.2-Adhikaraṇavaggo.json")
    
    if not file_path.exists():
        print(f"Error: File {file_path} not found")
        return
    
    print(f"Updating fixed file in Turso database: {file_path}")
    
    if update_chapter_in_database(file_path):
        print("\n✓ Database update completed successfully!")
    else:
        print("\n✗ Database update failed!")

if __name__ == "__main__":
    main()