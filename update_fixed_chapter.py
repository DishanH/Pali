#!/usr/bin/env python3
"""
Script to update the fixed chapter in Turso database
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def update_chapter_in_turso(file_path):
    """
    Update a specific chapter file in the Turso database
    """
    # Get database credentials
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("❌ Error: TURSO_DB_URL and TURSO_AUTH_TOKEN must be set in .env file")
        return False
    
    try:
        # Load the fixed JSON data
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        # Connect to database
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✓ Connected to Turso database")
        
        chapter_id = chapter_data['id']
        print(f"Updating chapter {chapter_id} in database...")
        
        # Update the chapter title and footer
        try:
            client.execute_query("""
                UPDATE chapters 
                SET title_pali = ?, title_english = ?, title_sinhala = ?
                WHERE id = ?
            """, [
                chapter_data['title']['pali'],
                chapter_data['title']['english'], 
                chapter_data['title']['sinhala'],
                chapter_id
            ])
            print(f"  ✓ Updated chapter metadata")
        except Exception as e:
            print(f"  ⚠️  Chapter metadata update failed: {e}")
        
        # Update sections
        sections_updated = 0
        sections_skipped = 0
        
        for section in chapter_data['sections']:
            section_number = section['number']
            
            try:
                # Update section content
                result = client.execute_query("""
                    UPDATE sections 
                    SET pali = ?, english = ?, sinhala = ?, pali_title = ?
                    WHERE chapter_id = ? AND section_number = ?
                """, [
                    section['pali'],
                    section['english'],
                    section['sinhala'],
                    section.get('paliTitle', ''),
                    chapter_id,
                    section_number
                ])
                
                sections_updated += 1
                
            except Exception as e:
                print(f"    ❌ Section {section_number} update failed: {e}")
                sections_skipped += 1
        
        print(f"  ✓ Updated {sections_updated} sections")
        if sections_skipped > 0:
            print(f"  ⚠️  Skipped {sections_skipped} sections due to errors")
            
        print(f"✅ Successfully updated chapter {chapter_id} in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating database for {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Main function to update the fixed file in database
    """
    # The specific file we fixed
    file_path = Path("Aṅguttaranikāyo/Dukanipātapāḷi/chapters/an2.2-Adhikaraṇavaggo.json")
    
    if not file_path.exists():
        print(f"❌ Error: File {file_path} not found")
        return
    
    print("=" * 60)
    print("Updating Fixed Chapter in Turso Database")
    print("=" * 60)
    print(f"File: {file_path}")
    
    if update_chapter_in_turso(file_path):
        print("\n🎉 Database update completed successfully!")
    else:
        print("\n❌ Database update failed!")

if __name__ == "__main__":
    main()