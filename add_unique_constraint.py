"""
Add unique constraint to sections table to prevent duplicate entries
This ensures each section_number within a chapter can only exist once
"""

import os
import sys
from dotenv import load_dotenv

try:
    import libsql_experimental as libsql
except ImportError:
    print("❌ libsql_experimental not found!")
    print("Please install: pip install libsql-experimental")
    sys.exit(1)

load_dotenv()

TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")


def add_unique_constraint():
    """Add unique constraint to prevent duplicate sections"""
    
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        print("❌ Error: Environment variables not set!")
        sys.exit(1)
    
    print("="*80)
    print("ADDING UNIQUE CONSTRAINT TO SECTIONS TABLE")
    print("="*80)
    
    try:
        conn = libsql.connect(database=TURSO_DB_URL, auth_token=TURSO_AUTH_TOKEN)
        cursor = conn.cursor()
        print("✓ Connected to Turso database")
        
        # Check if constraint already exists
        print("\n📋 Checking for existing constraint...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' 
            AND name='idx_sections_unique'
        """)
        
        existing = cursor.fetchone()
        
        if existing:
            print("⚠️  Unique constraint already exists!")
            print("   Index name: idx_sections_unique")
            conn.close()
            return
        
        # Add the unique constraint
        print("\n🔧 Adding unique constraint...")
        print("   This will prevent duplicate (chapter_id, section_number) entries")
        
        cursor.execute("""
            CREATE UNIQUE INDEX idx_sections_unique 
            ON sections(chapter_id, section_number)
        """)
        
        conn.commit()
        
        print("✅ Unique constraint added successfully!")
        print("\n📝 Details:")
        print("   Index name: idx_sections_unique")
        print("   Columns: (chapter_id, section_number)")
        print("   Effect: Prevents duplicate section numbers within the same chapter")
        
        # Verify
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='index' 
            AND name='idx_sections_unique'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"\n✓ Verification successful:")
            print(f"   {result[1]}")
        
        conn.close()
        print("\n✓ Database connection closed")
        
        print("\n" + "="*80)
        print("IMPORTANT NOTES")
        print("="*80)
        print("1. This constraint will prevent future duplicate imports")
        print("2. You must remove existing duplicates BEFORE adding this constraint")
        print("3. Run 'python remove_duplicate_sections_from_db.py' first if needed")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
        if "UNIQUE constraint failed" in str(e) or "duplicate" in str(e).lower():
            print("\n⚠️  Cannot add constraint - duplicates exist in the database!")
            print("\n📝 Steps to fix:")
            print("   1. Run: python remove_duplicate_sections_from_db.py")
            print("   2. Remove all duplicates")
            print("   3. Run this script again")
        
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    add_unique_constraint()
