#!/usr/bin/env python3
"""
DIRECT UNICODE FIX - Simplified for production use
Fixes Unicode issues with minimal complexity
"""

import json
import re
import os
from pathlib import Path
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def fix_unicode_text(text):
    """
    Fix all Unicode issues in text
    """
    if not text:
        return text, 0
    
    fixes = 0
    
    # 1. Fix #zwj; placeholders
    if '#zwj;' in text:
        count = text.count('#zwj;')
        text = text.replace('#zwj;', '\u200D')
        fixes += count
    
    # 2. Fix &zwj; HTML entities
    if '&zwj;' in text:
        count = text.count('&zwj;')
        text = text.replace('&zwj;', '\u200D')
        fixes += count
    
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
    
    text = re.sub(r'\{U\+([0-9A-Fa-f]+)\}', replace_unicode_literal, text)
    
    # 4. Fix Unicode escapes
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
    
    # 5. Clean excessive ZWJ
    excessive = re.findall(r'\u200D{2,}', text)
    if excessive:
        fixes += sum(len(match) - 1 for match in excessive)
        text = re.sub(r'\u200D{2,}', '\u200D', text)
    
    return text, fixes

def fix_json_file(file_path):
    """
    Fix Unicode issues in a JSON file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_fixes = 0
        
        def fix_recursive(obj):
            nonlocal total_fixes
            if isinstance(obj, dict):
                return {k: fix_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [fix_recursive(item) for item in obj]
            elif isinstance(obj, str):
                fixed_text, fixes = fix_unicode_text(obj)
                total_fixes += fixes
                return fixed_text
            else:
                return obj
        
        fixed_data = fix_recursive(data)
        
        if total_fixes > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(fixed_data, f, ensure_ascii=False, indent=2)
        
        return True, total_fixes
        
    except Exception as e:
        return False, 0

def update_database_chapter(file_path, client):
    """
    Update chapter in database
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data['id']
        
        # Update chapter
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
        
        # Update sections
        sections_updated = 0
        for section in chapter_data['sections']:
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
                section['number']
            ])
            sections_updated += 1
        
        return True, sections_updated
        
    except Exception as e:
        return False, 0

def main():
    """
    Main function - direct fix
    """
    print("=" * 60)
    print("DIRECT UNICODE FIX FOR PRODUCTION")
    print("=" * 60)
    
    # Find files
    json_files = []
    for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            json_files.extend(dir_path.rglob("*.json"))
    
    print(f"📁 Found {len(json_files)} files")
    
    # Fix files
    fixed_files = []
    total_fixes = 0
    
    print("\n🔧 Fixing files...")
    for i, file_path in enumerate(json_files, 1):
        if i % 50 == 0:
            print(f"   Progress: {i}/{len(json_files)}")
        
        success, fixes = fix_json_file(file_path)
        if success and fixes > 0:
            fixed_files.append(file_path)
            total_fixes += fixes
            print(f"  ✅ {file_path.name}: {fixes} fixes")
    
    print(f"\n📊 RESULTS:")
    print(f"   Files fixed: {len(fixed_files)}")
    print(f"   Total fixes: {total_fixes}")
    
    if not fixed_files:
        print("✅ No files needed fixing!")
        return
    
    # Update database
    response = input(f"\nUpdate database for {len(fixed_files)} files? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Database update skipped")
        return
    
    # Database update
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("❌ Database credentials not found")
        return
    
    try:
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✅ Connected to database")
        
        db_updated = 0
        for file_path in fixed_files:
            if 'chapters' in str(file_path):
                success, sections = update_database_chapter(file_path, client)
                if success:
                    print(f"  ✅ DB: {file_path.name} - {sections} sections")
                    db_updated += 1
                else:
                    print(f"  ❌ DB: {file_path.name} - failed")
        
        print(f"\n🎉 COMPLETED!")
        print(f"   Files fixed: {len(fixed_files)}")
        print(f"   Database updated: {db_updated}")
        print(f"   Total fixes: {total_fixes}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    main()