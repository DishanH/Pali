#!/usr/bin/env python3
"""
Script to execute the numberRange migration on Turso database.
This script requires libsql-experimental to be installed.

Run this after ensuring libsql-experimental is installed:
  pip install libsql-experimental python-dotenv
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import libsql_experimental as libsql
except ImportError:
    print("Error: libsql-experimental is not installed.")
    print("\nPlease install it first:")
    print("  pip install libsql-experimental python-dotenv")
    print("\nAlternatively, you can run the SQL files manually:")
    print("  1. add_number_range_migration.sql")
    print("  2. number_range_updates.sql")
    exit(1)

def get_turso_connection():
    """Create and return a Turso database connection."""
    url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")
    
    if not url or not auth_token:
        raise ValueError("TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set in .env file")
    
    return libsql.connect(database=url, auth_token=auth_token)

def execute_migration(conn):
    """Execute the migration to add number_range column."""
    cursor = conn.cursor()
    
    print("Step 1: Adding number_range column...")
    try:
        cursor.execute("ALTER TABLE sections ADD COLUMN number_range TEXT")
        conn.commit()
        print("✓ Column added successfully")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("✓ Column already exists")
        else:
            raise e
    
    # Add index
    print("\nStep 2: Creating index...")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_number_range ON sections(number_range)")
        conn.commit()
        print("✓ Index created successfully")
    except Exception as e:
        print(f"⚠ Index creation: {e}")

def execute_updates(conn):
    """Execute the UPDATE statements from the generated SQL file."""
    cursor = conn.cursor()
    
    print("\nStep 3: Updating sections with numberRange values...")
    
    # Read the SQL file
    with open('number_range_updates.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Extract UPDATE statements
    statements = [line.strip() for line in sql_content.split('\n') 
                  if line.strip().startswith('UPDATE')]
    
    print(f"Found {len(statements)} UPDATE statements to execute...")
    
    updated_count = 0
    for i, statement in enumerate(statements, 1):
        try:
            cursor.execute(statement)
            if cursor.rowcount > 0:
                updated_count += 1
            
            if i % 20 == 0:
                print(f"  Progress: {i}/{len(statements)} statements executed...")
        except Exception as e:
            print(f"  ✗ Error on statement {i}: {e}")
            print(f"    Statement: {statement[:100]}...")
    
    conn.commit()
    print(f"\n✓ Successfully updated {updated_count} sections")
    return updated_count

def verify_migration(conn):
    """Verify the migration was successful."""
    cursor = conn.cursor()
    
    print("\nStep 4: Verifying migration...")
    
    # Check column exists
    cursor.execute("PRAGMA table_info(sections)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'number_range' not in columns:
        print("✗ Column 'number_range' not found!")
        return False
    
    print("✓ Column 'number_range' exists")
    
    # Count sections with number_range
    cursor.execute("SELECT COUNT(*) FROM sections WHERE number_range IS NOT NULL")
    count = cursor.fetchone()[0]
    print(f"✓ Found {count} sections with number_range values")
    
    # Show some examples
    cursor.execute("""
        SELECT chapter_id, section_number, number_range 
        FROM sections 
        WHERE number_range IS NOT NULL
        LIMIT 5
    """)
    
    print("\nSample entries:")
    print(f"{'Chapter ID':<15} {'Section':<10} {'Number Range':<15}")
    print("-" * 40)
    for row in cursor.fetchall():
        print(f"{row[0]:<15} {row[1]:<10} {row[2]:<15}")
    
    return True

def main():
    """Main execution function."""
    print("="*60)
    print("Executing numberRange Migration on Turso Database")
    print("="*60)
    print()
    
    try:
        # Connect to database
        print("Connecting to Turso database...")
        conn = get_turso_connection()
        print("✓ Connected successfully\n")
        
        # Execute migration
        execute_migration(conn)
        
        # Execute updates
        updated_count = execute_updates(conn)
        
        # Verify
        if verify_migration(conn):
            print("\n" + "="*60)
            print("✓ Migration completed successfully!")
            print(f"  Total sections updated: {updated_count}")
            print("="*60)
        else:
            print("\n⚠ Migration completed with warnings")
        
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
