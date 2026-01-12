"""
Remove duplicate section entries from Turso database
This script identifies and removes duplicate sections, keeping only the first occurrence
"""

import os
import sys
from dotenv import load_dotenv

# Try to import database library
try:
    import libsql_experimental as libsql
    DB_LIB = "libsql_experimental"
except ImportError:
    print("❌ libsql_experimental not found!")
    print("Please install: pip install libsql-experimental")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configuration
TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")


class DuplicateRemover:
    def __init__(self, db_url, auth_token):
        """Initialize connection to Turso database"""
        if not db_url or not auth_token:
            raise ValueError("TURSO_DB_URL and TURSO_AUTH_TOKEN must be set")
        
        self.conn = libsql.connect(database=db_url, auth_token=auth_token)
        self.cursor = self.conn.cursor()
        print("✓ Connected to Turso database")
    
    def find_duplicates(self):
        """Find all duplicate sections"""
        print("\n" + "="*80)
        print("FINDING DUPLICATE SECTIONS IN DATABASE")
        print("="*80)
        
        self.cursor.execute("""
            SELECT 
                chapter_id,
                section_number,
                COUNT(*) as count,
                GROUP_CONCAT(id) as section_ids
            FROM sections
            GROUP BY chapter_id, section_number
            HAVING COUNT(*) > 1
            ORDER BY chapter_id, section_number
        """)
        
        duplicates = self.cursor.fetchall()
        
        if not duplicates:
            print("✅ No duplicate sections found in database!")
            return []
        
        print(f"\n⚠️  Found {len(duplicates)} duplicate section entries:\n")
        
        duplicate_list = []
        for chapter_id, section_num, count, section_ids in duplicates:
            # Get chapter details
            self.cursor.execute("""
                SELECT c.title_pali, c.title_english, b.name_pali, col.name_pali
                FROM chapters c
                JOIN books b ON c.book_id = b.id
                JOIN collections col ON b.collection_id = col.id
                WHERE c.id = ?
            """, (chapter_id,))
            
            chapter_info = self.cursor.fetchone()
            if chapter_info:
                chapter_title_pali, chapter_title_eng, book_name, collection_name = chapter_info
            else:
                chapter_title_pali = chapter_title_eng = book_name = collection_name = "Unknown"
            
            ids = [int(sid) for sid in section_ids.split(',')]
            
            duplicate_list.append({
                'chapter_id': chapter_id,
                'section_number': section_num,
                'count': count,
                'collection': collection_name,
                'book': book_name,
                'chapter_pali': chapter_title_pali,
                'chapter_english': chapter_title_eng,
                'section_ids': ids
            })
            
            print(f"Chapter: {chapter_id}")
            print(f"  Collection: {collection_name}")
            print(f"  Book: {book_name}")
            print(f"  Chapter: {chapter_title_pali} ({chapter_title_eng})")
            print(f"  Section Number: {section_num}")
            print(f"  Duplicate Count: {count}")
            print(f"  Section IDs: {ids}")
            print()
        
        return duplicate_list
    
    def remove_duplicates(self, duplicates, dry_run=True):
        """Remove duplicate sections, keeping only the first (lowest ID)"""
        
        if not duplicates:
            print("No duplicates to remove.")
            return
        
        print("\n" + "="*80)
        if dry_run:
            print("DRY RUN - NO CHANGES WILL BE MADE")
        else:
            print("REMOVING DUPLICATE SECTIONS")
        print("="*80)
        
        total_removed = 0
        
        for dup in duplicates:
            chapter_id = dup['chapter_id']
            section_num = dup['section_number']
            section_ids = sorted(dup['section_ids'])  # Sort to keep the first one
            
            # Keep the first ID, remove the rest
            keep_id = section_ids[0]
            remove_ids = section_ids[1:]
            
            print(f"\nChapter: {chapter_id}, Section: {section_num}")
            print(f"  Keeping ID: {keep_id}")
            print(f"  Removing IDs: {remove_ids}")
            
            if not dry_run:
                for remove_id in remove_ids:
                    try:
                        self.cursor.execute("DELETE FROM sections WHERE id = ?", (remove_id,))
                        total_removed += 1
                        print(f"    ✅ Deleted section ID {remove_id}")
                    except Exception as e:
                        print(f"    ❌ Error deleting section ID {remove_id}: {e}")
        
        if not dry_run:
            self.conn.commit()
            print(f"\n✅ Removed {total_removed} duplicate sections")
        else:
            print(f"\n📝 Would remove {sum(len(d['section_ids']) - 1 for d in duplicates)} duplicate sections")
    
    def verify_no_duplicates(self):
        """Verify that no duplicates remain"""
        print("\n" + "="*80)
        print("VERIFYING NO DUPLICATES REMAIN")
        print("="*80)
        
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT chapter_id, section_number, COUNT(*) as count
                FROM sections
                GROUP BY chapter_id, section_number
                HAVING COUNT(*) > 1
            )
        """)
        
        duplicate_count = self.cursor.fetchone()[0]
        
        if duplicate_count == 0:
            print("✅ No duplicates found - database is clean!")
            return True
        else:
            print(f"⚠️  Still found {duplicate_count} duplicate entries")
            return False
    
    def get_stats(self):
        """Get database statistics"""
        self.cursor.execute("SELECT COUNT(*) FROM sections")
        total_sections = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(DISTINCT chapter_id) FROM sections")
        total_chapters = self.cursor.fetchone()[0]
        
        print("\n" + "="*80)
        print("DATABASE STATISTICS")
        print("="*80)
        print(f"Total sections: {total_sections}")
        print(f"Total chapters with sections: {total_chapters}")
        print("="*80)
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("\n✓ Database connection closed")


def main():
    """Main function"""
    print("="*80)
    print("TURSO DATABASE DUPLICATE SECTION REMOVER")
    print("="*80)
    
    # Check environment variables
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        print("\n❌ Error: Environment variables not set!")
        print("\nPlease set:")
        print("  TURSO_DB_URL=your_database_url")
        print("  TURSO_AUTH_TOKEN=your_auth_token")
        sys.exit(1)
    
    try:
        # Initialize remover
        remover = DuplicateRemover(TURSO_DB_URL, TURSO_AUTH_TOKEN)
        
        # Show current stats
        remover.get_stats()
        
        # Find duplicates
        duplicates = remover.find_duplicates()
        
        if not duplicates:
            remover.close()
            return
        
        # First do a dry run
        print("\n" + "="*80)
        print("STEP 1: DRY RUN")
        print("="*80)
        remover.remove_duplicates(duplicates, dry_run=True)
        
        # Ask for confirmation
        print("\n" + "="*80)
        response = input("\nProceed with removing duplicates? (yes/no): ").strip().lower()
        
        if response == "yes":
            print("\n" + "="*80)
            print("STEP 2: REMOVING DUPLICATES")
            print("="*80)
            remover.remove_duplicates(duplicates, dry_run=False)
            
            # Verify
            remover.verify_no_duplicates()
            
            # Show final stats
            remover.get_stats()
        else:
            print("\n❌ Operation cancelled")
        
        # Close connection
        remover.close()
        
        print("\n✅ Done!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
