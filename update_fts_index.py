#!/usr/bin/env python3
"""
Update FTS Index Script
Rebuilds the sections_fts table to include vagga and title fields
"""

import os
from libsql_experimental import connect

def update_fts_index():
    """Update the FTS index with vagga and title fields"""
    
    # Get Turso credentials from environment
    turso_url = os.getenv('TURSO_DATABASE_URL')
    turso_token = os.getenv('TURSO_AUTH_TOKEN')
    
    if not turso_url or not turso_token:
        print("❌ Error: TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set")
        return False
    
    print("🔄 Connecting to Turso database...")
    conn = connect(database=turso_url, auth_token=turso_token)
    cursor = conn.cursor()
    
    try:
        # Read the update script
        with open('update_fts_index.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split into individual statements
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"📝 Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            print(f"   [{i}/{len(statements)}] Executing statement...")
            cursor.execute(statement)
        
        conn.commit()
        
        # Verify the update
        print("\n✅ Verifying FTS index...")
        cursor.execute("SELECT COUNT(*) FROM sections_fts")
        fts_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sections")
        sections_count = cursor.fetchone()[0]
        
        print(f"   Sections table: {sections_count} rows")
        print(f"   FTS index: {fts_count} rows")
        
        if fts_count == sections_count:
            print("\n✅ FTS index successfully updated!")
            print("   Now includes: vagga, vagga_english, vagga_sinhala, pali_title, english_title, sinhala_title")
            return True
        else:
            print(f"\n⚠️  Warning: Row count mismatch (sections: {sections_count}, FTS: {fts_count})")
            return False
            
    except Exception as e:
        print(f"\n❌ Error updating FTS index: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("FTS Index Update Script")
    print("=" * 60)
    print()
    
    success = update_fts_index()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Update completed successfully!")
    else:
        print("❌ Update failed. Please check the errors above.")
    print("=" * 60)
