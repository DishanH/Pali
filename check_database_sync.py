#!/usr/bin/env python3
"""
Check if database is in sync with JSON files
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def check_chapter_sync(file_path, client):
    """
    Check if a chapter file is in sync with database
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
        
        chapter_id = chapter_data['id']
        
        # Check first section as sample
        if not chapter_data['sections']:
            return True, "No sections to check"
        
        first_section = chapter_data['sections'][0]
        section_number = first_section['number']
        
        # Get from database
        result = client.execute_query("""
            SELECT sinhala 
            FROM sections 
            WHERE chapter_id = ? AND section_number = ?
        """, [chapter_id, section_number])
        
        if not result.get('results'):
            return False, "No database results"
        
        rows = result['results'][0]['response']['result']['rows']
        if not rows:
            return False, "Section not found in database"
        
        db_sinhala = rows[0][0]
        if isinstance(db_sinhala, dict):
            db_sinhala = db_sinhala.get('value', '')
        
        file_sinhala = first_section['sinhala']
        
        # Compare (first 200 chars)
        db_preview = db_sinhala[:200] if db_sinhala else ""
        file_preview = file_sinhala[:200] if file_sinhala else ""
        
        if db_preview == file_preview:
            return True, "In sync"
        else:
            return False, f"Mismatch:\nDB: {db_preview}...\nFile: {file_preview}..."
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """
    Check database sync status
    """
    print("=" * 60)
    print("DATABASE SYNC CHECK")
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
    
    # Find sample files to check
    json_files = []
    for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            chapter_files = list(dir_path.rglob("chapters/*.json"))[:5]  # Just first 5 from each
            json_files.extend(chapter_files)
    
    print(f"📁 Checking {len(json_files)} sample files...")
    
    in_sync = 0
    out_of_sync = 0
    
    for file_path in json_files:
        sync_status, message = check_chapter_sync(file_path, client)
        
        if sync_status:
            print(f"✅ {file_path.name}: {message}")
            in_sync += 1
        else:
            print(f"❌ {file_path.name}: {message}")
            out_of_sync += 1
    
    print(f"\n📊 RESULTS:")
    print(f"   In sync: {in_sync}")
    print(f"   Out of sync: {out_of_sync}")
    
    if out_of_sync > 0:
        print(f"\n⚠️  Database appears to be out of sync with JSON files!")
        print(f"   Run fix_database_update_issue.py to fix this.")
    else:
        print(f"\n✅ Database appears to be in sync!")

if __name__ == "__main__":
    main()