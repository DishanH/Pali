#!/usr/bin/env python3
"""
Fix the database update issue in direct_unicode_fix.py
This script will properly update the database with transaction management
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def update_database_chapter_fixed(file_path, client):
    """
    Update chapter in database with proper error handling and verification
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data['id']
        print(f"  📝 Updating chapter: {chapter_id}")
        
        # Update chapter title
        try:
            result = client.execute_query("""
                UPDATE chapters 
                SET title_pali = ?, title_english = ?, title_sinhala = ?
                WHERE id = ?
            """, [
                chapter_data['title']['pali'],
                chapter_data['title']['english'], 
                chapter_data['title']['sinhala'],
                chapter_id
            ])
            print(f"    ✅ Chapter title updated")
        except Exception as e:
            print(f"    ❌ Chapter title update failed: {e}")
        
        # Update sections one by one with verification
        sections_updated = 0
        sections_failed = 0
        
        for section in chapter_data['sections']:
            try:
                # Check if section exists first
                check_result = client.execute_query("""
                    SELECT COUNT(*) as count 
                    FROM sections 
                    WHERE chapter_id = ? AND section_number = ?
                """, [chapter_id, section['number']])
                
                if check_result.get('results'):
                    count = check_result['results'][0]['response']['result']['rows'][0][0]
                    if isinstance(count, dict):
                        count = count.get('value', 0)
                    
                    if count > 0:
                        # Update existing section
                        update_result = client.execute_query("""
                            UPDATE sections 
                            SET pali = ?, english = ?, sinhala = ?, pali_title = ?, english_title = ?, sinhala_title = ?
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
                        sections_updated += 1
                        print(f"    ✅ Section {section['number']} updated")
                    else:
                        print(f"    ⚠️  Section {section['number']} not found in database")
                        sections_failed += 1
                else:
                    print(f"    ❌ Could not check section {section['number']}")
                    sections_failed += 1
                    
            except Exception as e:
                print(f"    ❌ Section {section['number']} update failed: {e}")
                sections_failed += 1
        
        # Update footer if exists
        if 'footer' in chapter_data:
            try:
                footer_result = client.execute_query("""
                    UPDATE chapters 
                    SET footer_pali = ?, footer_english = ?, footer_sinhala = ?
                    WHERE id = ?
                """, [
                    chapter_data['footer']['pali'],
                    chapter_data['footer']['english'],
                    chapter_data['footer']['sinhala'],
                    chapter_id
                ])
                print(f"    ✅ Footer updated")
            except Exception as e:
                print(f"    ❌ Footer update failed: {e}")
        
        return True, sections_updated, sections_failed
        
    except Exception as e:
        print(f"    ❌ Chapter update failed: {e}")
        return False, 0, 0

def verify_database_update(file_path, client):
    """
    Verify that the database was actually updated
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data['id']
        
        # Check a few sections to verify updates
        sample_sections = chapter_data['sections'][:3]  # Check first 3 sections
        
        for section in sample_sections:
            result = client.execute_query("""
                SELECT sinhala 
                FROM sections 
                WHERE chapter_id = ? AND section_number = ?
            """, [chapter_id, section['number']])
            
            if result.get('results'):
                db_sinhala = result['results'][0]['response']['result']['rows'][0][0]
                if isinstance(db_sinhala, dict):
                    db_sinhala = db_sinhala.get('value', '')
                
                file_sinhala = section['sinhala']
                
                if db_sinhala != file_sinhala:
                    print(f"    ⚠️  Mismatch in section {section['number']}")
                    print(f"       DB:   {db_sinhala[:100]}...")
                    print(f"       File: {file_sinhala[:100]}...")
                    return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Verification failed: {e}")
        return False

def main():
    """
    Fix database updates for all files that were processed by direct_unicode_fix.py
    """
    print("=" * 60)
    print("FIXING DATABASE UPDATE ISSUES")
    print("=" * 60)
    
    # Get database connection
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("❌ Database credentials not found in .env file")
        return
    
    try:
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✅ Connected to Turso database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Find all JSON chapter files
    json_files = []
    for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            chapter_files = list(dir_path.rglob("chapters/*.json"))
            json_files.extend(chapter_files)
    
    print(f"📁 Found {len(json_files)} chapter files")
    
    if not json_files:
        print("❌ No chapter files found")
        return
    
    # Ask for confirmation
    response = input(f"\nUpdate database for all {len(json_files)} files? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Operation cancelled")
        return
    
    # Process files
    print(f"\n🔄 Processing {len(json_files)} files...")
    
    total_updated = 0
    total_failed = 0
    total_sections = 0
    
    for i, file_path in enumerate(json_files, 1):
        print(f"\n[{i}/{len(json_files)}] {file_path.name}")
        
        success, sections_updated, sections_failed = update_database_chapter_fixed(file_path, client)
        
        if success:
            # Verify the update
            if verify_database_update(file_path, client):
                print(f"    ✅ Verified: {sections_updated} sections updated")
                total_updated += 1
                total_sections += sections_updated
            else:
                print(f"    ⚠️  Update completed but verification failed")
                total_failed += 1
        else:
            print(f"    ❌ Update failed")
            total_failed += 1
    
    # Final summary
    print(f"\n" + "=" * 60)
    print(f"FINAL RESULTS:")
    print(f"=" * 60)
    print(f"✅ Files successfully updated: {total_updated}")
    print(f"❌ Files failed: {total_failed}")
    print(f"📊 Total sections updated: {total_sections}")
    print(f"=" * 60)

if __name__ == "__main__":
    main()