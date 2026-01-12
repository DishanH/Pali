#!/usr/bin/env python3
"""
Comprehensive script to find and fix all binary data issues in JSON files
and update them in the Turso database
"""

import json
import re
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def fix_binary_data_in_text(text):
    """
    Fix binary data markers in text by replacing them with proper Unicode characters
    """
    if not text:
        return text
    
    # Common patterns we can identify from Sinhala text
    fixes = [
        # ප්‍රතිසංඛ pattern
        (r'ප<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>තිසංඛ', 'ප්‍රතිසංඛ'),
        # ප්‍රහාණ pattern  
        (r'ප<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>හාණ', 'ප්‍රහාණ'),
        # ශෛක්‍ෂ pattern
        (r'ශෛක<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>ෂ', 'ශෛක්‍ෂ'),
        # General patterns - try to reconstruct common Sinhala conjuncts
        (r'<binary data, 1 bytes><binary data, 1 bytes><binary data, 1 bytes>', '්‍ර'),
        (r'<binary data, 1 bytes><binary data, 1 bytes>', '්‍'),
        (r'<binary data, 1 bytes>', '්'),
    ]
    
    result = text
    for pattern, replacement in fixes:
        result = re.sub(pattern, replacement, result)
    
    return result

def fix_json_file(file_path):
    """
    Fix binary data issues in a JSON file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if file has binary data issues
        content_str = json.dumps(data, ensure_ascii=False)
        if '<binary data, 1 bytes>' not in content_str:
            return False, "No binary data issues found"
        
        # Recursively fix all string values in the JSON
        def fix_recursive(obj):
            if isinstance(obj, dict):
                return {k: fix_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [fix_recursive(item) for item in obj]
            elif isinstance(obj, str):
                return fix_binary_data_in_text(obj)
            else:
                return obj
        
        fixed_data = fix_recursive(data)
        
        # Write back the fixed data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=2)
        
        return True, "Fixed successfully"
        
    except Exception as e:
        return False, f"Error: {e}"

def update_chapter_in_database(file_path, client):
    """
    Update a chapter in the Turso database
    """
    try:
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
        return False, f"Database update error: {e}"

def main():
    """
    Main function to comprehensively fix binary data issues
    """
    print("=" * 70)
    print("Comprehensive Binary Data Fix for Pali Tipitaka")
    print("=" * 70)
    
    # Find all JSON files
    json_files = []
    
    # Search in all collection directories
    for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            json_files.extend(dir_path.rglob("*.json"))
    
    if not json_files:
        print("❌ No JSON files found to process")
        return
    
    print(f"📁 Found {len(json_files)} JSON files to check")
    
    # Check for binary data issues
    files_with_issues = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '<binary data, 1 bytes>' in content:
                    files_with_issues.append(json_file)
        except Exception as e:
            print(f"⚠️  Error reading {json_file}: {e}")
    
    if not files_with_issues:
        print("✅ No binary data issues found in any files!")
        return
    
    print(f"🔍 Found {len(files_with_issues)} files with binary data issues:")
    for file_path in files_with_issues:
        print(f"  - {file_path}")
    
    # Fix the files
    print(f"\n🔧 Fixing {len(files_with_issues)} files...")
    fixed_files = []
    
    for file_path in files_with_issues:
        success, message = fix_json_file(file_path)
        if success:
            print(f"  ✓ {file_path.name}: {message}")
            fixed_files.append(file_path)
        else:
            print(f"  ❌ {file_path.name}: {message}")
    
    if not fixed_files:
        print("❌ No files were successfully fixed")
        return
    
    print(f"\n✅ Successfully fixed {len(fixed_files)} files")
    
    # Update database
    print(f"\n🗄️  Updating database...")
    
    # Get database credentials
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("⚠️  Database credentials not found. Skipping database update.")
        print("   Files have been fixed locally.")
        return
    
    try:
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✓ Connected to Turso database")
        
        db_updated_count = 0
        for file_path in fixed_files:
            # Only update chapter files (not book.json files)
            if file_path.name != 'book.json' and 'chapters' in str(file_path):
                success, message = update_chapter_in_database(file_path, client)
                if success:
                    print(f"  ✓ Database updated for {file_path.name}: {message}")
                    db_updated_count += 1
                else:
                    print(f"  ❌ Database update failed for {file_path.name}: {message}")
        
        print(f"\n✅ Database updated for {db_updated_count} chapters")
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("   Files have been fixed locally, but database was not updated.")
    
    print("\n" + "=" * 70)
    print("🎉 Comprehensive binary data fix completed!")
    print(f"   Files fixed: {len(fixed_files)}")
    print(f"   Database updated: {db_updated_count if 'db_updated_count' in locals() else 0}")
    print("=" * 70)

if __name__ == "__main__":
    main()