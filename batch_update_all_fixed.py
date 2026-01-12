#!/usr/bin/env python3
"""
Script to batch update all files that were fixed for Unicode escape sequences
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def update_chapter_in_database(file_path, client):
    """
    Update a specific chapter file in the Turso database
    """
    try:
        # Load the JSON data
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data['id']
        
        # Update the chapter title and footer
        client.execute_query("""
            UPDATE chapters 
            SET title_pali = ?, title_english = ?, title_sinhala = ?,
                footer_pali = ?, footer_english = ?, footer_sinhala = ?
            WHERE id = ?
        """, [
            chapter_data['title']['pali'],
            chapter_data['title']['english'], 
            chapter_data['title']['sinhala'],
            chapter_data.get('footer', {}).get('pali', ''),
            chapter_data.get('footer', {}).get('english', ''),
            chapter_data.get('footer', {}).get('sinhala', ''),
            chapter_id
        ])
        
        # Update sections
        sections_updated = 0
        for section in chapter_data['sections']:
            section_number = section['number']
            
            client.execute_query("""
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
        
        return True, f"Updated {sections_updated} sections"
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """
    Main function to batch update all fixed files
    """
    print("=" * 70)
    print("Batch Update All Fixed Files to Turso Database")
    print("=" * 70)
    
    # Get database credentials
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("❌ Error: TURSO_DB_URL and TURSO_AUTH_TOKEN must be set in .env file")
        return
    
    try:
        # Connect to database
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✓ Connected to Turso database")
        
        # Find all chapter JSON files (not book.json files)
        chapter_files = []
        
        # Search in all collection directories
        for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
            dir_path = Path(directory)
            if dir_path.exists():
                # Find chapter files in chapters subdirectories
                for chapter_file in dir_path.rglob("chapters/*.json"):
                    chapter_files.append(chapter_file)
        
        if not chapter_files:
            print("❌ No chapter files found to update")
            return
        
        print(f"📁 Found {len(chapter_files)} chapter files to update")
        
        # Update files in batches
        updated_count = 0
        failed_count = 0
        
        for i, file_path in enumerate(chapter_files, 1):
            print(f"\n[{i}/{len(chapter_files)}] Updating: {file_path.name}")
            
            success, message = update_chapter_in_database(file_path, client)
            if success:
                print(f"  ✓ {message}")
                updated_count += 1
            else:
                print(f"  ❌ {message}")
                failed_count += 1
            
            # Commit every 10 updates to avoid large transactions
            if i % 10 == 0:
                print(f"  💾 Committing batch {i//10}...")
        
        print(f"\n" + "=" * 70)
        print(f"📊 Update Summary:")
        print(f"   Total files processed: {len(chapter_files)}")
        print(f"   Successfully updated: {updated_count}")
        print(f"   Failed updates: {failed_count}")
        print(f"=" * 70)
        
        if updated_count > 0:
            print("\n🎉 Batch update completed successfully!")
        else:
            print("\n❌ No files were successfully updated")
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()