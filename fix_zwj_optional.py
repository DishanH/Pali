#!/usr/bin/env python3
"""
OPTIONAL: Fix #zwj placeholders in JSON files and database
WARNING: This makes permanent changes. Use with caution!
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def fix_zwj_in_text(text):
    """
    Fix #zwj placeholders by replacing with actual ZWJ character
    """
    if not text:
        return text
    
    # Replace #zwj; with actual Zero Width Joiner (U+200D)
    return text.replace('#zwj;', '\u200D')

def fix_zwj_in_json_file(file_path, dry_run=True):
    """
    Fix #zwj placeholders in a JSON file
    
    Args:
        file_path: Path to JSON file
        dry_run: If True, only show what would be changed
    
    Returns:
        (bool, str, int): (success, message, zwj_count)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if file has #zwj issues
        content_str = json.dumps(data, ensure_ascii=False)
        zwj_count = content_str.count('#zwj;')
        
        if zwj_count == 0:
            return True, "No #zwj issues found", 0
        
        if dry_run:
            return True, f"Would fix {zwj_count} #zwj occurrences", zwj_count
        
        # Recursively fix all string values
        def fix_recursive(obj):
            if isinstance(obj, dict):
                return {k: fix_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [fix_recursive(item) for item in obj]
            elif isinstance(obj, str):
                return fix_zwj_in_text(obj)
            else:
                return obj
        
        fixed_data = fix_recursive(data)
        
        # Write back the fixed data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=2)
        
        return True, f"Fixed {zwj_count} #zwj occurrences", zwj_count
        
    except Exception as e:
        return False, f"Error: {e}", 0

def update_chapter_in_database(file_path, client):
    """
    Update a chapter in the Turso database with fixed ZWJ
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data['id']
        
        # Update the chapter title and footer
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
        return False, f"Database error: {e}"

def main():
    """
    Main function - OPTIONAL ZWJ fix
    """
    print("=" * 70)
    print("OPTIONAL: ZWJ Placeholder Fix")
    print("⚠️  WARNING: This makes permanent changes to files and database!")
    print("=" * 70)
    
    # Get user confirmation
    print("\n🤔 Do you want to proceed? This will:")
    print("   1. Replace all #zwj; with actual ZWJ characters (\\u200D)")
    print("   2. Update JSON files permanently")
    print("   3. Update database with fixed text")
    print("\n💡 Alternative: Use zwj_handler.py for display-time cleaning (RECOMMENDED)")
    
    response = input("\nProceed with permanent fix? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("❌ Operation cancelled. Use zwj_handler.py for safe display-time cleaning.")
        return
    
    # First, do a dry run
    print("\n🔍 Performing dry run analysis...")
    
    # Find files with ZWJ issues
    json_files = []
    for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            json_files.extend(dir_path.rglob("chapters/*.json"))
    
    files_to_fix = []
    total_zwj = 0
    
    for json_file in json_files:
        success, message, zwj_count = fix_zwj_in_json_file(json_file, dry_run=True)
        if zwj_count > 0:
            files_to_fix.append((json_file, zwj_count))
            total_zwj += zwj_count
            print(f"  📄 {json_file.name}: {zwj_count} #zwj occurrences")
    
    if not files_to_fix:
        print("✅ No files need ZWJ fixing!")
        return
    
    print(f"\n📊 Summary:")
    print(f"   Files to fix: {len(files_to_fix)}")
    print(f"   Total #zwj occurrences: {total_zwj}")
    
    # Final confirmation
    final_confirm = input(f"\nFix {len(files_to_fix)} files with {total_zwj} #zwj occurrences? (yes/no): ").lower().strip()
    
    if final_confirm != 'yes':
        print("❌ Operation cancelled.")
        return
    
    # Fix files
    print(f"\n🔧 Fixing files...")
    fixed_files = []
    
    for file_path, expected_count in files_to_fix:
        success, message, actual_count = fix_zwj_in_json_file(file_path, dry_run=False)
        if success and actual_count > 0:
            print(f"  ✅ {file_path.name}: {message}")
            fixed_files.append(file_path)
        else:
            print(f"  ❌ {file_path.name}: {message}")
    
    # Update database
    if fixed_files:
        print(f"\n🗄️  Updating database...")
        
        # Get database credentials
        db_url = os.getenv("TURSO_DB_URL", "")
        auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
        
        if not db_url or not auth_token:
            print("⚠️  Database credentials not found. Files fixed but database not updated.")
            return
        
        try:
            client = TursoClient(database_url=db_url, auth_token=auth_token)
            print("✅ Connected to database")
            
            db_updated = 0
            for file_path in fixed_files:
                success, message = update_chapter_in_database(file_path, client)
                if success:
                    print(f"  ✅ Database: {file_path.name} - {message}")
                    db_updated += 1
                else:
                    print(f"  ❌ Database: {file_path.name} - {message}")
            
            print(f"\n🎉 ZWJ fix completed!")
            print(f"   Files fixed: {len(fixed_files)}")
            print(f"   Database updated: {db_updated}")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("   Files were fixed but database was not updated.")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Test text rendering in your application")
    print(f"   2. Verify Sinhala conjunct characters display correctly")
    print(f"   3. Keep backups of original files if needed")

if __name__ == "__main__":
    main()