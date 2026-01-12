#!/usr/bin/env python3
"""
Script to add numberRange column to the sections table and update entries
that have this field in the JSON files.
"""

import os
import json
import libsql_experimental as libsql
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def get_turso_connection():
    """Create and return a Turso database connection."""
    url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")
    
    if not url or not auth_token:
        raise ValueError("TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set in .env file")
    
    return libsql.connect(database=url, auth_token=auth_token)

def add_number_range_column(conn):
    """Add numberRange column to sections table if it doesn't exist."""
    try:
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(sections)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'number_range' in columns:
            print("✓ Column 'number_range' already exists in sections table")
            return True
        
        # Add the column
        print("Adding 'number_range' column to sections table...")
        cursor.execute("""
            ALTER TABLE sections 
            ADD COLUMN number_range TEXT
        """)
        conn.commit()
        print("✓ Successfully added 'number_range' column")
        return True
        
    except Exception as e:
        print(f"✗ Error adding column: {e}")
        return False

def find_json_files():
    """Find all chapter JSON files in the directory structure."""
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

def update_sections_with_number_range(conn):
    """Update sections table with numberRange data from JSON files."""
    cursor = conn.cursor()
    json_files = find_json_files()
    
    total_updated = 0
    total_with_range = 0
    
    print(f"\nScanning {len(json_files)} JSON files...")
    
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
                    total_with_range += 1
                    
                    # Update the database
                    cursor.execute("""
                        UPDATE sections 
                        SET number_range = ? 
                        WHERE chapter_id = ? AND section_number = ?
                    """, (number_range, chapter_id, section_number))
                    
                    if cursor.rowcount > 0:
                        total_updated += 1
                        print(f"  ✓ Updated {chapter_id} section {section_number}: {number_range}")
                    else:
                        print(f"  ⚠ No match found for {chapter_id} section {section_number}")
            
        except Exception as e:
            print(f"  ✗ Error processing {json_file}: {e}")
            continue
    
    conn.commit()
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total sections with numberRange in JSON: {total_with_range}")
    print(f"  Total sections updated in database: {total_updated}")
    print(f"{'='*60}")
    
    return total_updated

def verify_updates(conn):
    """Verify the updates by querying sections with number_range."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT chapter_id, section_number, number_range 
        FROM sections 
        WHERE number_range IS NOT NULL
        ORDER BY chapter_id, section_number
    """)
    
    results = cursor.fetchall()
    
    if results:
        print(f"\n✓ Verification: Found {len(results)} sections with number_range:")
        print(f"\n{'Chapter ID':<20} {'Section':<10} {'Number Range':<20}")
        print(f"{'-'*50}")
        for row in results[:10]:  # Show first 10
            print(f"{row[0]:<20} {row[1]:<10} {row[2]:<20}")
        
        if len(results) > 10:
            print(f"... and {len(results) - 10} more")
    else:
        print("\n⚠ No sections found with number_range")

def main():
    """Main execution function."""
    print("="*60)
    print("Adding numberRange column to sections table")
    print("="*60)
    
    try:
        # Connect to database
        print("\nConnecting to Turso database...")
        conn = get_turso_connection()
        print("✓ Connected successfully")
        
        # Add column
        if not add_number_range_column(conn):
            return
        
        # Update sections
        total_updated = update_sections_with_number_range(conn)
        
        # Verify
        if total_updated > 0:
            verify_updates(conn)
        
        print("\n✓ Process completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()
            print("\n✓ Database connection closed")

if __name__ == "__main__":
    main()
