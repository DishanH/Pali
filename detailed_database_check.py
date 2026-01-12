#!/usr/bin/env python3
"""
Detailed check of specific database entries
"""

import json
import os
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def check_specific_chapter(chapter_id, client):
    """
    Check specific chapter in detail
    """
    print(f"\n🔍 Checking chapter: {chapter_id}")
    
    # Get chapter info
    result = client.execute_query("""
        SELECT title_sinhala, COUNT(*) as section_count
        FROM chapters c
        LEFT JOIN sections s ON c.id = s.chapter_id
        WHERE c.id = ?
        GROUP BY c.id, c.title_sinhala
    """, [chapter_id])
    
    if result.get('results'):
        rows = result['results'][0]['response']['result']['rows']
        if rows:
            title = rows[0][0]
            if isinstance(title, dict):
                title = title.get('value', '')
            count = rows[0][1]
            if isinstance(count, dict):
                count = count.get('value', 0)
            print(f"  📖 Title: {title}")
            print(f"  📊 Sections: {count}")
        else:
            print(f"  ❌ Chapter not found in database")
            return
    
    # Get sample sections
    sections_result = client.execute_query("""
        SELECT section_number, sinhala_title, 
               SUBSTR(sinhala, 1, 100) as sinhala_preview
        FROM sections 
        WHERE chapter_id = ? 
        ORDER BY section_number 
        LIMIT 3
    """, [chapter_id])
    
    if sections_result.get('results'):
        rows = sections_result['results'][0]['response']['result']['rows']
        print(f"  📝 Sample sections:")
        for row in rows:
            section_num = row[0]
            if isinstance(section_num, dict):
                section_num = section_num.get('value', '')
            
            sinhala_title = row[1]
            if isinstance(sinhala_title, dict):
                sinhala_title = sinhala_title.get('value', '')
            
            sinhala_preview = row[2]
            if isinstance(sinhala_preview, dict):
                sinhala_preview = sinhala_preview.get('value', '')
            
            print(f"    {section_num}: {sinhala_title}")
            print(f"       {sinhala_preview}...")

def check_unicode_fixes(client):
    """
    Check for Unicode issues in database
    """
    print(f"\n🔍 Checking for Unicode issues in database...")
    
    # Check for #zwj; placeholders
    result = client.execute_query("""
        SELECT chapter_id, section_number, 'sinhala' as field
        FROM sections 
        WHERE sinhala LIKE '%#zwj;%'
        LIMIT 5
    """)
    
    if result.get('results'):
        rows = result['results'][0]['response']['result']['rows']
        if rows:
            print(f"  ❌ Found #zwj; placeholders in {len(rows)} sections:")
            for row in rows:
                chapter_id = row[0]
                if isinstance(chapter_id, dict):
                    chapter_id = chapter_id.get('value', '')
                section_num = row[1]
                if isinstance(section_num, dict):
                    section_num = section_num.get('value', '')
                print(f"    {chapter_id} section {section_num}")
        else:
            print(f"  ✅ No #zwj; placeholders found")
    
    # Check for &zwj; entities
    result = client.execute_query("""
        SELECT chapter_id, section_number
        FROM sections 
        WHERE sinhala LIKE '%&zwj;%'
        LIMIT 5
    """)
    
    if result.get('results'):
        rows = result['results'][0]['response']['result']['rows']
        if rows:
            print(f"  ❌ Found &zwj; entities in {len(rows)} sections")
        else:
            print(f"  ✅ No &zwj; entities found")
    
    # Check for Unicode escapes
    result = client.execute_query("""
        SELECT chapter_id, section_number
        FROM sections 
        WHERE sinhala LIKE '%\\u%'
        LIMIT 5
    """)
    
    if result.get('results'):
        rows = result['results'][0]['response']['result']['rows']
        if rows:
            print(f"  ❌ Found Unicode escapes in {len(rows)} sections")
        else:
            print(f"  ✅ No Unicode escapes found")

def main():
    """
    Detailed database check
    """
    print("=" * 60)
    print("DETAILED DATABASE CHECK")
    print("=" * 60)
    
    # Get database connection
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("❌ Database credentials not found")
        return
    
    try:
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Check specific chapters
    test_chapters = ["an4.13", "an8.1", "dn.2.1", "mn.2.1"]
    
    for chapter_id in test_chapters:
        check_specific_chapter(chapter_id, client)
    
    # Check for Unicode issues
    check_unicode_fixes(client)
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()