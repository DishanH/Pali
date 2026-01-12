#!/usr/bin/env python3
"""
Final comprehensive Unicode fix for all remaining issues
"""

import os
import re
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def comprehensive_unicode_fix(text):
    """
    Comprehensive Unicode fix for all patterns
    """
    if not text:
        return text, 0
    
    fixes = 0
    original_text = text
    
    # 1. Fix #zwj; placeholders
    if '#zwj;' in text:
        count = text.count('#zwj;')
        text = text.replace('#zwj;', '\u200D')
        fixes += count
        print(f"    Fixed {count} #zwj; placeholders")
    
    # 2. Fix &zwj; HTML entities
    if '&zwj;' in text:
        count = text.count('&zwj;')
        text = text.replace('&zwj;', '\u200D')
        fixes += count
        print(f"    Fixed {count} &zwj; entities")
    
    # 3. Fix {U+200D} literal notation
    def replace_unicode_literal(match):
        nonlocal fixes
        try:
            hex_code = match.group(1)
            char_code = int(hex_code, 16)
            fixes += 1
            return chr(char_code)
        except:
            return match.group(0)
    
    before_count = len(re.findall(r'\{U\+([0-9A-Fa-f]+)\}', text))
    text = re.sub(r'\{U\+([0-9A-Fa-f]+)\}', replace_unicode_literal, text)
    if before_count > 0:
        print(f"    Fixed {before_count} Unicode literals")
    
    # 4. Fix ALL Unicode escapes (comprehensive list)
    unicode_escapes = {
        '\\u0DCA': '\u0DCA',  # Sinhala Virama
        '\\u200D': '\u200D',  # Zero Width Joiner
        '\\u200C': '\u200C',  # Zero Width Non-Joiner
        '\\u0D9A': '\u0D9A',  # Sinhala Ka
        '\\u0DBB': '\u0DBB',  # Sinhala Ra
        '\\u0DBA': '\u0DBA',  # Sinhala Ya
        '\\u0DB8': '\u0DB8',  # Sinhala Ma
        '\\u0D9C': '\u0D9C',  # Sinhala Ga
        '\\u0DAD': '\u0DAD',  # Sinhala Ta
        '\\u0DB1': '\u0DB1',  # Sinhala Na
        '\\u0DC4': '\u0DC4',  # Sinhala Ha
        '\\u0DC0': '\u0DC0',  # Sinhala Va
        '\\u0DC3': '\u0DC3',  # Sinhala Sa
        '\\u0DC5': '\u0DC5',  # Sinhala La
        '\\u0D85': '\u0D85',  # Sinhala A
        '\\u0D87': '\u0D87',  # Sinhala Aa
        '\\u0D89': '\u0D89',  # Sinhala I
        '\\u0D8B': '\u0D8B',  # Sinhala Ii
        '\\u0D8D': '\u0D8D',  # Sinhala U
        '\\u0D8F': '\u0D8F',  # Sinhala Uu
        '\\u0D91': '\u0D91',  # Sinhala E
        '\\u0D93': '\u0D93',  # Sinhala Ee
        '\\u0D94': '\u0D94',  # Sinhala O
        '\\u0D96': '\u0D96',  # Sinhala Oo
    }
    
    escape_fixes = 0
    for escape, char in unicode_escapes.items():
        if escape in text:
            count = text.count(escape)
            text = text.replace(escape, char)
            fixes += count
            escape_fixes += count
    
    if escape_fixes > 0:
        print(f"    Fixed {escape_fixes} Unicode escapes")
    
    # 5. Fix any remaining \\uXXXX patterns (generic)
    def replace_generic_unicode(match):
        nonlocal fixes
        try:
            hex_code = match.group(1)
            char_code = int(hex_code, 16)
            fixes += 1
            return chr(char_code)
        except:
            return match.group(0)
    
    remaining_escapes = re.findall(r'\\u([0-9A-Fa-f]{4})', text)
    if remaining_escapes:
        print(f"    Found additional Unicode escapes: {set(remaining_escapes)}")
        text = re.sub(r'\\u([0-9A-Fa-f]{4})', replace_generic_unicode, text)
    
    # 6. Clean excessive ZWJ sequences
    excessive_zwj = re.findall(r'\u200D{2,}', text)
    if excessive_zwj:
        count = sum(len(match) - 1 for match in excessive_zwj)
        text = re.sub(r'\u200D{2,}', '\u200D', text)
        fixes += count
        print(f"    Fixed {count} excessive ZWJ sequences")
    
    return text, fixes

def fix_all_unicode_issues(client):
    """Fix all Unicode issues in database"""
    
    print("🔍 Finding ALL sections with Unicode issues...")
    
    # Get all sections with any Unicode issues
    result = client.execute_query("""
        SELECT chapter_id, section_number, sinhala
        FROM sections 
        WHERE sinhala LIKE '%#zwj;%' 
           OR sinhala LIKE '%&zwj;%'
           OR sinhala LIKE '%\\u%'
           OR sinhala LIKE '%{U+%'
    """)
    
    if not result.get('results'):
        print("✅ No Unicode issues found!")
        return 0
    
    rows = result['results'][0]['response']['result']['rows']
    print(f"📊 Found {len(rows)} sections with Unicode issues")
    
    total_fixes = 0
    
    for i, row in enumerate(rows, 1):
        chapter_id = row[0]
        if isinstance(chapter_id, dict):
            chapter_id = chapter_id.get('value', '')
        section_num = row[1]
        if isinstance(section_num, dict):
            section_num = section_num.get('value', '')
        sinhala = row[2]
        if isinstance(sinhala, dict):
            sinhala = sinhala.get('value', '')
        
        print(f"\n[{i}/{len(rows)}] Fixing {chapter_id} section {section_num}")
        
        fixed_text, fixes = comprehensive_unicode_fix(sinhala)
        
        if fixes > 0:
            # Update database
            client.execute_query("""
                UPDATE sections 
                SET sinhala = ?
                WHERE chapter_id = ? AND section_number = ?
            """, [fixed_text, chapter_id, section_num])
            
            print(f"  ✅ Applied {fixes} total fixes")
            total_fixes += fixes
        else:
            print(f"  ℹ️  No fixes needed")
    
    return total_fixes

def main():
    """Final comprehensive Unicode fix"""
    
    print("=" * 60)
    print("FINAL COMPREHENSIVE UNICODE FIX")
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
    
    # Fix all issues
    total_fixes = fix_all_unicode_issues(client)
    
    print(f"\n🎉 COMPLETED!")
    print(f"   Total fixes applied: {total_fixes}")
    
    # Final verification
    print(f"\n🔍 Final verification...")
    
    result = client.execute_query("""
        SELECT COUNT(*) as count
        FROM sections 
        WHERE sinhala LIKE '%#zwj;%' 
           OR sinhala LIKE '%&zwj;%'
           OR sinhala LIKE '%\\u%'
           OR sinhala LIKE '%{U+%'
    """)
    
    if result.get('results'):
        count = result['results'][0]['response']['result']['rows'][0][0]
        if isinstance(count, dict):
            count = count.get('value', 0)
        
        if count == 0:
            print(f"✅ ALL Unicode issues have been fixed!")
        else:
            print(f"⚠️  {count} sections still have Unicode issues")
            print(f"   These may be edge cases that need manual review")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()