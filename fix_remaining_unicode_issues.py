#!/usr/bin/env python3
"""
Fix the remaining Unicode issues found in the database
"""

import os
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def fix_unicode_text(text):
    """Fix Unicode issues in text"""
    if not text:
        return text, 0
    
    fixes = 0
    original = text
    
    # Fix #zwj; placeholders
    if '#zwj;' in text:
        count = text.count('#zwj;')
        text = text.replace('#zwj;', '\u200D')
        fixes += count
    
    # Fix Unicode escapes
    escapes = {
        '\\u0DCA': '\u0DCA',
        '\\u200D': '\u200D',
        '\\u200C': '\u200C',
        '\\u0D9A': '\u0D9A',
        '\\u0DBB': '\u0DBB',
        '\\u0DBA': '\u0DBA',
        '\\u0DB8': '\u0DB8',
    }
    
    for escape, char in escapes.items():
        if escape in text:
            count = text.count(escape)
            text = text.replace(escape, char)
            fixes += count
    
    return text, fixes

def fix_remaining_issues(client):
    """Fix remaining Unicode issues in database"""
    
    print("🔍 Finding sections with Unicode issues...")
    
    # Find sections with #zwj; placeholders
    result = client.execute_query("""
        SELECT chapter_id, section_number, sinhala
        FROM sections 
        WHERE sinhala LIKE '%#zwj;%'
    """)
    
    zwj_sections = []
    if result.get('results'):
        rows = result['results'][0]['response']['result']['rows']
        for row in rows:
            chapter_id = row[0]
            if isinstance(chapter_id, dict):
                chapter_id = chapter_id.get('value', '')
            section_num = row[1]
            if isinstance(section_num, dict):
                section_num = section_num.get('value', '')
            sinhala = row[2]
            if isinstance(sinhala, dict):
                sinhala = sinhala.get('value', '')
            zwj_sections.append((chapter_id, section_num, sinhala))
    
    # Find sections with Unicode escapes
    result = client.execute_query("""
        SELECT chapter_id, section_number, sinhala
        FROM sections 
        WHERE sinhala LIKE '%\\u%'
    """)
    
    escape_sections = []
    if result.get('results'):
        rows = result['results'][0]['response']['result']['rows']
        for row in rows:
            chapter_id = row[0]
            if isinstance(chapter_id, dict):
                chapter_id = chapter_id.get('value', '')
            section_num = row[1]
            if isinstance(section_num, dict):
                section_num = section_num.get('value', '')
            sinhala = row[2]
            if isinstance(sinhala, dict):
                sinhala = sinhala.get('value', '')
            escape_sections.append((chapter_id, section_num, sinhala))
    
    print(f"📊 Found {len(zwj_sections)} sections with #zwj; placeholders")
    print(f"📊 Found {len(escape_sections)} sections with Unicode escapes")
    
    # Fix #zwj; sections
    for chapter_id, section_num, sinhala in zwj_sections:
        fixed_text, fixes = fix_unicode_text(sinhala)
        if fixes > 0:
            client.execute_query("""
                UPDATE sections 
                SET sinhala = ?
                WHERE chapter_id = ? AND section_number = ?
            """, [fixed_text, chapter_id, section_num])
            print(f"  ✅ Fixed {chapter_id} section {section_num}: {fixes} #zwj; fixes")
    
    # Fix Unicode escape sections
    for chapter_id, section_num, sinhala in escape_sections:
        fixed_text, fixes = fix_unicode_text(sinhala)
        if fixes > 0:
            client.execute_query("""
                UPDATE sections 
                SET sinhala = ?
                WHERE chapter_id = ? AND section_number = ?
            """, [fixed_text, chapter_id, section_num])
            print(f"  ✅ Fixed {chapter_id} section {section_num}: {fixes} escape fixes")
    
    return len(zwj_sections) + len(escape_sections)

def main():
    """Fix remaining Unicode issues"""
    
    print("=" * 60)
    print("FIXING REMAINING UNICODE ISSUES")
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
    
    # Fix remaining issues
    fixed_count = fix_remaining_issues(client)
    
    print(f"\n✅ Fixed {fixed_count} sections with Unicode issues")
    
    # Verify fixes
    print(f"\n🔍 Verifying fixes...")
    
    result = client.execute_query("""
        SELECT COUNT(*) as count
        FROM sections 
        WHERE sinhala LIKE '%#zwj;%' OR sinhala LIKE '%\\u%'
    """)
    
    if result.get('results'):
        count = result['results'][0]['response']['result']['rows'][0][0]
        if isinstance(count, dict):
            count = count.get('value', 0)
        
        if count == 0:
            print(f"✅ All Unicode issues fixed!")
        else:
            print(f"⚠️  {count} sections still have Unicode issues")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()