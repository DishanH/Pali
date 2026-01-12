#!/usr/bin/env python3
"""
Comprehensive Sinhala Language Fix
Fixes all Unicode and ZWJ issues in both JSON files and database
"""

import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def comprehensive_sinhala_fix(text):
    """
    Comprehensive fix for all Sinhala Unicode issues
    """
    if not text:
        return text, 0
    
    original_text = text
    fixes = 0
    
    # 1. Fix all ZWJ-related issues
    zwj_patterns = [
        ('#zwj;', '\u200D'),
        ('#ZWJ;', '\u200D'),
        ('&zwj;', '\u200D'),
        ('&ZWJ;', '\u200D'),
    ]
    
    for pattern, replacement in zwj_patterns:
        if pattern in text:
            count = text.count(pattern)
            text = text.replace(pattern, replacement)
            fixes += count
    
    # 2. Fix Unicode escapes (comprehensive list)
    unicode_escapes = {
        '\\u200D': '\u200D',  # Zero Width Joiner
        '\\u200C': '\u200C',  # Zero Width Non-Joiner
        '\\u0DCA': '\u0DCA',  # Sinhala Virama (Al-Lakuna)
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
        '\\u0D9A': '\u0D9A',  # Sinhala Ka
        '\\u0D9B': '\u0D9B',  # Sinhala Kha
        '\\u0D9C': '\u0D9C',  # Sinhala Ga
        '\\u0D9D': '\u0D9D',  # Sinhala Gha
        '\\u0D9E': '\u0D9E',  # Sinhala Nga
        '\\u0D9F': '\u0D9F',  # Sinhala Ca
        '\\u0DA0': '\u0DA0',  # Sinhala Cha
        '\\u0DA1': '\u0DA1',  # Sinhala Ja
        '\\u0DA2': '\u0DA2',  # Sinhala Jha
        '\\u0DA3': '\u0DA3',  # Sinhala Nya
        '\\u0DA4': '\u0DA4',  # Sinhala Tta
        '\\u0DA5': '\u0DA5',  # Sinhala Ttha
        '\\u0DA6': '\u0DA6',  # Sinhala Dda
        '\\u0DA7': '\u0DA7',  # Sinhala Ddha
        '\\u0DA8': '\u0DA8',  # Sinhala Nna
        '\\u0DA9': '\u0DA9',  # Sinhala Ndda
        '\\u0DAA': '\u0DAA',  # Sinhala Nndda
        '\\u0DAB': '\u0DAB',  # Sinhala Ta
        '\\u0DAC': '\u0DAC',  # Sinhala Tha
        '\\u0DAD': '\u0DAD',  # Sinhala Da
        '\\u0DAE': '\u0DAE',  # Sinhala Dha
        '\\u0DAF': '\u0DAF',  # Sinhala Na
        '\\u0DB0': '\u0DB0',  # Sinhala Nda
        '\\u0DB1': '\u0DB1',  # Sinhala Nda
        '\\u0DB3': '\u0DB3',  # Sinhala Pa
        '\\u0DB4': '\u0DB4',  # Sinhala Pha
        '\\u0DB5': '\u0DB5',  # Sinhala Ba
        '\\u0DB6': '\u0DB6',  # Sinhala Bha
        '\\u0DB7': '\u0DB7',  # Sinhala Ma
        '\\u0DB8': '\u0DB8',  # Sinhala Mba
        '\\u0DB9': '\u0DB9',  # Sinhala Ya
        '\\u0DBA': '\u0DBA',  # Sinhala Ra
        '\\u0DBB': '\u0DBB',  # Sinhala Ra
        '\\u0DBC': '\u0DBC',  # Sinhala La
        '\\u0DBD': '\u0DBD',  # Sinhala La
        '\\u0DC0': '\u0DC0',  # Sinhala Va
        '\\u0DC1': '\u0DC1',  # Sinhala Sha
        '\\u0DC2': '\u0DC2',  # Sinhala Ssa
        '\\u0DC3': '\u0DC3',  # Sinhala Sa
        '\\u0DC4': '\u0DC4',  # Sinhala Ha
        '\\u0DC5': '\u0DC5',  # Sinhala Lla
        '\\u0DC6': '\u0DC6',  # Sinhala Fa
        # Vowel signs
        '\\u0DCF': '\u0DCF',  # Sinhala Vowel Sign Aela-Pilla
        '\\u0DD0': '\u0DD0',  # Sinhala Vowel Sign Ketti Aeda-Pilla
        '\\u0DD1': '\u0DD1',  # Sinhala Vowel Sign Diga Aeda-Pilla
        '\\u0DD2': '\u0DD2',  # Sinhala Vowel Sign Ketti Is-Pilla
        '\\u0DD3': '\u0DD3',  # Sinhala Vowel Sign Diga Is-Pilla
        '\\u0DD4': '\u0DD4',  # Sinhala Vowel Sign Ketti Paa-Pilla
        '\\u0DD6': '\u0DD6',  # Sinhala Vowel Sign Diga Paa-Pilla
        '\\u0DD8': '\u0DD8',  # Sinhala Vowel Sign Gaetta-Pilla
        '\\u0DD9': '\u0DD9',  # Sinhala Vowel Sign Kombuva
        '\\u0DDA': '\u0DDA',  # Sinhala Vowel Sign Diga Kombuva
        '\\u0DDB': '\u0DDB',  # Sinhala Vowel Sign Kombu Deka
        '\\u0DDC': '\u0DDC',  # Sinhala Vowel Sign Kombuva Haa Aela-Pilla
        '\\u0DDD': '\u0DDD',  # Sinhala Vowel Sign Kombuva Haa Diga Aela-Pilla
        '\\u0DDE': '\u0DDE',  # Sinhala Vowel Sign Kombuva Haa Gayanukitta
        '\\u0DDF': '\u0DDF',  # Sinhala Vowel Sign Gayanukitta
    }
    
    for escape, char in unicode_escapes.items():
        if escape in text:
            count = text.count(escape)
            text = text.replace(escape, char)
            fixes += count
    
    # 3. Fix {U+XXXX} literal notation
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
    
    # 4. Fix any remaining \\uXXXX patterns (generic)
    def replace_generic_unicode(match):
        nonlocal fixes
        try:
            hex_code = match.group(1)
            char_code = int(hex_code, 16)
            fixes += 1
            return chr(char_code)
        except:
            return match.group(0)
    
    text = re.sub(r'\\u([0-9A-Fa-f]{4})', replace_generic_unicode, text)
    
    # 5. Clean excessive ZWJ sequences
    excessive_zwj = re.findall(r'\u200D{2,}', text)
    if excessive_zwj:
        count = sum(len(match) - 1 for match in excessive_zwj)
        text = re.sub(r'\u200D{2,}', '\u200D', text)
        fixes += count
    
    # 6. Fix specific Sinhala issues
    sinhala_fixes = [
        # Common ZWJ combinations that should be properly formed
        ('ත්\u200D\u200Dර', 'ත්‍ර'),  # tra
        ('ක්\u200D\u200Dර', 'ක්‍ර'),  # kra
        ('ප්\u200D\u200Dර', 'ප්‍ර'),  # pra
        ('ග්\u200D\u200Dර', 'ග්‍ර'),  # gra
        ('ද්\u200D\u200Dර', 'ද්‍ර'),  # dra
        ('බ්\u200D\u200Dර', 'බ්‍ර'),  # bra
        ('ම්\u200D\u200Dර', 'ම්‍ර'),  # mra
        ('ස්\u200D\u200Dර', 'ස්‍ර'),  # sra
        ('හ්\u200D\u200Dර', 'හ්‍ර'),  # hra
        ('ල්\u200D\u200Dර', 'ල්‍ර'),  # lra
        ('න්\u200D\u200Dර', 'න්‍ර'),  # nra
        ('ව්\u200D\u200Dර', 'ව්‍ර'),  # vra
        # Fix double ZWJ in other combinations
        ('්\u200D\u200D', '්‍'),  # Generic virama + double ZWJ
    ]
    
    for wrong, correct in sinhala_fixes:
        if wrong in text:
            count = text.count(wrong)
            text = text.replace(wrong, correct)
            fixes += count
    
    # 7. Normalize ZWJ usage - ensure proper ZWJ after virama
    # Fix cases where ZWJ is missing or incorrectly placed
    text = re.sub(r'්(?!\u200D)([කගටදනපබමයරලවසහ])', r'්‍\1', text)
    
    return text, fixes

def fix_json_file(file_path):
    """
    Fix all Unicode issues in a JSON file
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
                fixed_text, fixes = comprehensive_sinhala_fix(obj)
                total_fixes += fixes
                return fixed_text
            else:
                return obj
        
        fixed_data = fix_recursive(data)
        
        if total_fixes > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(fixed_data, f, ensure_ascii=False, indent=2)
            return True, total_fixes
        
        return False, 0
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False, 0

def update_database_chapter(file_path, client):
    """
    Update chapter in database with fixed content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data['id']
        
        # Update chapter title
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
            sections_updated += 1
        
        # Update footer if exists
        if 'footer' in chapter_data:
            client.execute_query("""
                UPDATE chapters 
                SET footer_pali = ?, footer_english = ?, footer_sinhala = ?
                WHERE id = ?
            """, [
                chapter_data['footer']['pali'],
                chapter_data['footer']['english'],
                chapter_data['footer']['sinhala'],
                chapter_id
            ])
        
        return True, sections_updated
        
    except Exception as e:
        print(f"Error updating database for {file_path}: {e}")
        return False, 0

def main():
    """
    Comprehensive Sinhala fix for all files and database
    """
    print("=" * 60)
    print("COMPREHENSIVE SINHALA LANGUAGE FIX")
    print("=" * 60)
    
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
    
    # Fix JSON files first
    print(f"\n🔧 Fixing JSON files...")
    
    fixed_files = []
    total_json_fixes = 0
    
    for i, file_path in enumerate(json_files, 1):
        if i % 50 == 0:
            print(f"   Progress: {i}/{len(json_files)}")
        
        success, fixes = fix_json_file(file_path)
        if success and fixes > 0:
            fixed_files.append(file_path)
            total_json_fixes += fixes
            print(f"  ✅ {file_path.name}: {fixes} fixes")
    
    print(f"\n📊 JSON FILES RESULTS:")
    print(f"   Files fixed: {len(fixed_files)}")
    print(f"   Total fixes: {total_json_fixes}")
    
    if not fixed_files:
        print("✅ No JSON files needed fixing!")
        return
    
    # Update database
    response = input(f"\nUpdate database for {len(fixed_files)} files? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Database update skipped")
        return
    
    # Get database connection
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("❌ Database credentials not found")
        return
    
    try:
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✅ Connected to Turso database")
        
        print(f"\n🔄 Updating database...")
        
        db_updated = 0
        total_sections = 0
        
        for i, file_path in enumerate(fixed_files, 1):
            print(f"[{i}/{len(fixed_files)}] Updating {file_path.name}")
            
            success, sections = update_database_chapter(file_path, client)
            if success:
                db_updated += 1
                total_sections += sections
                print(f"  ✅ Updated {sections} sections")
            else:
                print(f"  ❌ Failed to update")
        
        print(f"\n🎉 FINAL RESULTS:")
        print(f"   JSON files fixed: {len(fixed_files)}")
        print(f"   JSON fixes applied: {total_json_fixes}")
        print(f"   Database chapters updated: {db_updated}")
        print(f"   Database sections updated: {total_sections}")
        
        # Final verification
        print(f"\n🔍 Final verification...")
        
        result = client.execute_query("""
            SELECT COUNT(*) as count
            FROM sections 
            WHERE sinhala LIKE '%#zwj;%' 
               OR sinhala LIKE '%#ZWJ;%'
               OR sinhala LIKE '%&zwj;%'
               OR sinhala LIKE '%\\u%'
               OR sinhala LIKE '%{U+%'
        """)
        
        if result.get('results'):
            count = result['results'][0]['response']['result']['rows'][0][0]
            if isinstance(count, dict):
                count = count.get('value', 0)
            
            if count == 0:
                print(f"✅ ALL Sinhala language issues have been fixed!")
            else:
                print(f"⚠️  {count} sections still have Unicode issues")
                print(f"   These may need manual review")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()