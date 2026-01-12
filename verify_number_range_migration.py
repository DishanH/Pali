#!/usr/bin/env python3
"""
Verify which sections with numberRange are in the database.
"""

import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def get_turso_config():
    """Get Turso configuration from environment."""
    url = os.getenv("TURSO_DATABASE_URL") or os.getenv("TURSO_DB_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")
    
    if not url or not token:
        raise ValueError("Database credentials not found in .env")
    
    if url.startswith("libsql://"):
        url = url.replace("libsql://", "https://")
    
    return url, token

def execute_query(url, token, sql):
    """Execute a query and return results."""
    api_url = f"{url}/v2/pipeline"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "requests": [
            {"type": "execute", "stmt": {"sql": sql}}
        ]
    }
    
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    result = response.json()
    return result.get("results", [{}])[0]

def find_json_files():
    """Find all chapter JSON files."""
    json_files = []
    base_dirs = [
        "Aṅguttaranikāyo",
        "Dīghanikāyo",
        "Majjhimanikāye",
        "Saṃyuttanikāyo"
    ]
    
    for base_dir in base_dirs:
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.json') and 'chapters' in root:
                        json_files.append(os.path.join(root, file))
    
    return json_files

def get_expected_sections():
    """Get all sections with numberRange from JSON files."""
    json_files = find_json_files()
    expected = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chapter_id = data.get('id')
            if not chapter_id:
                continue
            
            sections = data.get('sections', [])
            
            for section in sections:
                section_number = section.get('number')
                number_range = section.get('numberRange')
                
                if number_range:
                    expected.append({
                        'chapter_id': chapter_id,
                        'section_number': section_number,
                        'number_range': number_range
                    })
        except Exception as e:
            continue
    
    return expected

def get_database_sections(url, token):
    """Get all sections with number_range from database."""
    result = execute_query(url, token, """
        SELECT chapter_id, section_number, number_range 
        FROM sections 
        WHERE number_range IS NOT NULL
        ORDER BY chapter_id, section_number
    """)
    
    rows = result.get("response", {}).get("result", {}).get("rows", [])
    db_sections = []
    
    for row in rows:
        db_sections.append({
            'chapter_id': row[0]["value"],
            'section_number': row[1]["value"],
            'number_range': row[2]["value"]
        })
    
    return db_sections

def main():
    print("="*60)
    print("NumberRange Migration Verification")
    print("="*60)
    print()
    
    try:
        # Get configuration
        url, token = get_turso_config()
        
        # Get expected sections from JSON
        print("Scanning JSON files...")
        expected = get_expected_sections()
        print(f"✓ Found {len(expected)} sections with numberRange in JSON files")
        
        # Get actual sections from database
        print("\nQuerying database...")
        db_sections = get_database_sections(url, token)
        print(f"✓ Found {len(db_sections)} sections with number_range in database")
        
        # Create lookup sets
        expected_keys = {(s['chapter_id'], s['section_number']) for s in expected}
        db_keys = {(s['chapter_id'], s['section_number']) for s in db_sections}
        
        # Find missing sections
        missing_keys = expected_keys - db_keys
        
        if missing_keys:
            print(f"\n⚠ {len(missing_keys)} sections are missing from database:")
            print(f"\n{'Chapter ID':<20} {'Section':<10}")
            print("-" * 30)
            
            missing_list = []
            for chapter_id, section_number in sorted(missing_keys):
                print(f"{chapter_id:<20} {section_number:<10}")
                # Find the full info
                for s in expected:
                    if s['chapter_id'] == chapter_id and s['section_number'] == section_number:
                        missing_list.append(s)
                        break
            
            # Save missing sections to file
            with open('missing_number_range_sections.json', 'w', encoding='utf-8') as f:
                json.dump(missing_list, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Missing sections saved to: missing_number_range_sections.json")
            
            # Generate SQL for missing sections
            with open('missing_number_range_updates.sql', 'w', encoding='utf-8') as f:
                f.write("-- UPDATE statements for missing numberRange sections\n\n")
                f.write("BEGIN TRANSACTION;\n\n")
                
                for s in missing_list:
                    chapter_id = s['chapter_id'].replace("'", "''")
                    number_range = s['number_range'].replace("'", "''")
                    sql = f"UPDATE sections SET number_range = '{number_range}' WHERE chapter_id = '{chapter_id}' AND section_number = {s['section_number']};\n"
                    f.write(sql)
                
                f.write("\nCOMMIT;\n")
            
            print(f"✓ SQL for missing sections saved to: missing_number_range_updates.sql")
        else:
            print("\n✓ All sections are present in the database!")
        
        # Find extra sections (in DB but not in JSON)
        extra_keys = db_keys - expected_keys
        if extra_keys:
            print(f"\n⚠ {len(extra_keys)} sections in database but not in JSON files:")
            for chapter_id, section_number in sorted(extra_keys):
                print(f"  {chapter_id} section {section_number}")
        
        # Summary
        print("\n" + "="*60)
        print("Summary:")
        print(f"  Expected (from JSON): {len(expected)}")
        print(f"  Found (in database): {len(db_sections)}")
        print(f"  Missing: {len(missing_keys)}")
        print(f"  Extra: {len(extra_keys)}")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
