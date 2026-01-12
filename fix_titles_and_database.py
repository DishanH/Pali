#!/usr/bin/env python3
"""
Fix specific Sinhala titles and update database with correct column names
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def fix_specific_titles():
    """
    Fix the specific titles mentioned by user
    """
    file_path = Path("Aṅguttaranikāyo/Catukkanipātapāḷi/chapters/an4.13-Bhayavaggo.json")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        changes_made = False
        
        # Check each section for the titles that need to be replaced
        for section in data['sections']:
            sinhala_title = section.get('sinhalaTitle', '')
            
            # Replace the specific titles
            if 'ආත්‍මාරෝපණ සූත්‍රය' in sinhala_title:
                section['sinhalaTitle'] = sinhala_title.replace('ආත්‍මාරෝපණ සූත්‍රය', 'අත්තානුවාද සූත්‍රය')
                print(f"  ✅ Section {section['number']}: Fixed ආත්‍මාරෝපණ → අත්තානුවාද")
                changes_made = True
            
            if 'උ‍ර්මිභය සූත‍්‍රය' in sinhala_title:
                section['sinhalaTitle'] = sinhala_title.replace('උ‍ර්මිභය සූත‍්‍රය', 'ඌමිභය සූත්‍රය')
                print(f"  ✅ Section {section['number']}: Fixed උ‍ර්මිභය → ඌමිභය")
                changes_made = True
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Updated file: {file_path.name}")
            return True
        else:
            print(f"ℹ️  No title changes needed in {file_path.name}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return False

def update_database_with_correct_schema():
    """
    Update database using correct column names
    """
    # Get database connection
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("❌ Database credentials not found")
        return False
    
    try:
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✅ Connected to database")
        
        # First, let's check the actual schema
        print("\n🔍 Checking database schema...")
        
        # Check chapters table
        result = client.execute_query("PRAGMA table_info(chapters)")
        if result.get('results'):
            rows = result['results'][0]['response']['result']['rows']
            print("📋 Chapters table columns:")
            for row in rows:
                col_name = row[1] if isinstance(row[1], str) else row[1].get('value', '')
                print(f"  - {col_name}")
        
        # Check sections table  
        result = client.execute_query("PRAGMA table_info(sections)")
        if result.get('results'):
            rows = result['results'][0]['response']['result']['rows']
            print("📋 Sections table columns:")
            for row in rows:
                col_name = row[1] if isinstance(row[1], str) else row[1].get('value', '')
                print(f"  - {col_name}")
        
        # Find all JSON files to update
        json_files = []
        for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
            dir_path = Path(directory)
            if dir_path.exists():
                chapter_files = list(dir_path.rglob("chapters/*.json"))
                json_files.extend(chapter_files)
        
        print(f"\n🔄 Updating database for {len(json_files)} files...")
        
        updated_chapters = 0
        updated_sections = 0
        
        for i, file_path in enumerate(json_files, 1):
            if i % 20 == 0:
                print(f"   Progress: {i}/{len(json_files)}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    chapter_data = json.load(f)
                
                chapter_id = chapter_data['id']
                
                # Update chapter with correct column names
                client.execute_query("""
                    UPDATE chapters 
                    SET pali_title = ?, english_title = ?, sinhala_title = ?
                    WHERE id = ?
                """, [
                    chapter_data['title']['pali'],
                    chapter_data['title']['english'], 
                    chapter_data['title']['sinhala'],
                    chapter_id
                ])
                
                # Update sections with correct column names
                for section in chapter_data['sections']:
                    client.execute_query("""
                        UPDATE sections 
                        SET pali = ?, english = ?, sinhala = ?, 
                            pali_title = ?, english_title = ?, sinhala_title = ?
                        WHERE chapter_id = ? AND section_number = ?
                    """, [
                        section['pali'],
                        section['english'],
                        section['sinhala'],
                        section.get('paliTitle', ''),
                        section.get('englishTitle', ''),
                        section.get('sinhalaTitle', ''),
                        chapter_id,
                        section['number']
                    ])
                    updated_sections += 1
                
                updated_chapters += 1
                
            except Exception as e:
                print(f"  ❌ Error updating {file_path.name}: {e}")
                continue
        
        print(f"\n🎉 Database update completed!")
        print(f"   Chapters updated: {updated_chapters}")
        print(f"   Sections updated: {updated_sections}")
        
        # Verify the specific title changes
        print(f"\n🔍 Verifying title changes...")
        
        result = client.execute_query("""
            SELECT chapter_id, section_number, sinhala_title
            FROM sections 
            WHERE chapter_id = 'an4.13' AND section_number IN (121, 122)
        """)
        
        if result.get('results'):
            rows = result['results'][0]['response']['result']['rows']
            for row in rows:
                chapter_id = row[0] if isinstance(row[0], str) else row[0].get('value', '')
                section_num = row[1] if isinstance(row[1], (str, int)) else row[1].get('value', '')
                title = row[2] if isinstance(row[2], str) else row[2].get('value', '')
                print(f"  📝 {chapter_id} section {section_num}: {title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """
    Main function
    """
    print("=" * 60)
    print("FIX TITLES AND DATABASE UPDATE")
    print("=" * 60)
    
    # Step 1: Fix specific titles in JSON files
    print("🔧 Step 1: Fixing specific titles...")
    title_changes = fix_specific_titles()
    
    # Step 2: Update database with correct schema
    print("\n🔧 Step 2: Updating database...")
    db_success = update_database_with_correct_schema()
    
    if db_success:
        print("\n✅ All tasks completed successfully!")
    else:
        print("\n⚠️  Some issues occurred during database update")

if __name__ == "__main__":
    main()