"""
Completely recreate the 3 chapters with duplicate sections
This script:
1. Deletes ALL sections for the 3 problematic chapters from the database
2. Re-imports them fresh from the JSON files
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

try:
    from libsql_client import create_client
    import asyncio
    USE_ASYNC = True
except ImportError:
    try:
        import libsql_experimental as libsql
        USE_ASYNC = False
    except ImportError:
        print("❌ No libsql library found!")
        print("Please install: pip install libsql-client")
        sys.exit(1)

load_dotenv()

TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

# The 3 files with duplicates
PROBLEM_CHAPTERS = [
    {
        'chapter_id': 'mn.3.1',
        'file_path': 'Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters/mn.3.1-Devadahavaggo.json',
        'description': 'Majjhima Nikāya - Devadahavaggo'
    },
    {
        'chapter_id': 'sn.2.1',
        'file_path': 'Saṃyuttanikāyo/Nidānavaggo/chapters/sn.2.1-Nidānasaṃyuttaṃ.json',
        'description': 'Saṃyutta Nikāya - Nidānasaṃyuttaṃ'
    },
    {
        'chapter_id': 'sn.4.1',
        'file_path': 'Saṃyuttanikāyo/Saḷāyatanavaggo/chapters/sn.4.1-Saḷāyatanasaṃyuttaṃ.json',
        'description': 'Saṃyutta Nikāya - Saḷāyatanasaṃyuttaṃ'
    }
]


class ChapterRecreator:
    def __init__(self, db_url, auth_token):
        """Initialize connection to Turso database"""
        if not db_url or not auth_token:
            raise ValueError("TURSO_DB_URL and TURSO_AUTH_TOKEN must be set")
        
        if USE_ASYNC:
            self.client = create_client(url=db_url, auth_token=auth_token)
            self.use_async = True
        else:
            self.conn = libsql.connect(database=db_url, auth_token=auth_token)
            self.cursor = self.conn.cursor()
            self.use_async = False
        print("✓ Connected to Turso database")
    
    async def _execute_async(self, query, params=None):
        """Execute async query"""
        if params:
            result = await self.client.execute(query, params)
        else:
            result = await self.client.execute(query)
        return result
    
    def execute(self, query, params=None):
        """Execute query (sync or async)"""
        if self.use_async:
            return asyncio.run(self._execute_async(query, params))
        else:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
    
    def get_section_count(self, chapter_id):
        """Get current section count for a chapter"""
        if self.use_async:
            result = self.execute("""
                SELECT COUNT(*) FROM sections WHERE chapter_id = ?
            """, [chapter_id])
            return result.rows[0][0] if result.rows else 0
        else:
            self.cursor.execute("""
                SELECT COUNT(*) FROM sections WHERE chapter_id = ?
            """, (chapter_id,))
            return self.cursor.fetchone()[0]
    
    def delete_all_sections(self, chapter_id):
        """Delete all sections for a chapter"""
        count = self.get_section_count(chapter_id)
        
        if count == 0:
            print(f"  ℹ️  No sections to delete")
            return 0
        
        print(f"  🗑️  Deleting {count} existing sections...")
        
        if self.use_async:
            self.execute("DELETE FROM sections WHERE chapter_id = ?", [chapter_id])
        else:
            self.cursor.execute("DELETE FROM sections WHERE chapter_id = ?", (chapter_id,))
            self.conn.commit()
        
        # Verify deletion
        remaining = self.get_section_count(chapter_id)
        if remaining == 0:
            print(f"  ✅ All sections deleted successfully")
            return count
        else:
            print(f"  ⚠️  Warning: {remaining} sections still remain")
            return count - remaining
    
    def insert_sections(self, chapter_id, sections):
        """Insert sections for a chapter"""
        print(f"  📥 Inserting {len(sections)} sections...")
        
        inserted = 0
        for section in sections:
            try:
                params = [
                    chapter_id,
                    section.get("number"),
                    section.get("pali", ""),
                    section.get("english", ""),
                    section.get("sinhala", ""),
                    section.get("paliTitle", ""),
                    section.get("englishTitle", ""),
                    section.get("sinhalaTitle", ""),
                    section.get("vagga", ""),
                    section.get("vaggaEnglish", ""),
                    section.get("vaggaSinhala", "")
                ]
                
                if self.use_async:
                    self.execute("""
                        INSERT INTO sections (
                            chapter_id, section_number, pali, english, sinhala,
                            pali_title, english_title, sinhala_title,
                            vagga, vagga_english, vagga_sinhala
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, params)
                else:
                    self.cursor.execute("""
                        INSERT INTO sections (
                            chapter_id, section_number, pali, english, sinhala,
                            pali_title, english_title, sinhala_title,
                            vagga, vagga_english, vagga_sinhala
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(params))
                
                inserted += 1
            except Exception as e:
                print(f"  ❌ Error inserting section {section.get('number')}: {e}")
        
        if not self.use_async:
            self.conn.commit()
        
        print(f"  ✅ Inserted {inserted} sections")
        return inserted
    
    def recreate_chapter(self, chapter_info, dry_run=True):
        """Recreate a chapter by deleting and re-importing"""
        chapter_id = chapter_info['chapter_id']
        file_path = Path(chapter_info['file_path'])
        description = chapter_info['description']
        
        print(f"\n{'='*80}")
        print(f"Chapter: {description}")
        print(f"ID: {chapter_id}")
        print(f"File: {file_path}")
        print(f"{'='*80}")
        
        # Check if file exists
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        # Read the JSON file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
        
        sections = data.get("sections", [])
        if not sections:
            print(f"⚠️  No sections found in file")
            return False
        
        print(f"📄 File contains {len(sections)} sections")
        
        # Get current count
        current_count = self.get_section_count(chapter_id)
        print(f"💾 Database currently has {current_count} sections")
        
        if dry_run:
            print(f"\n🔍 DRY RUN - Would perform:")
            print(f"  1. Delete {current_count} existing sections")
            print(f"  2. Insert {len(sections)} fresh sections from file")
            return True
        
        # Delete all existing sections
        deleted = self.delete_all_sections(chapter_id)
        
        # Insert fresh sections from file
        inserted = self.insert_sections(chapter_id, sections)
        
        # Verify
        final_count = self.get_section_count(chapter_id)
        print(f"\n📊 Summary:")
        print(f"  Deleted: {deleted}")
        print(f"  Inserted: {inserted}")
        print(f"  Final count: {final_count}")
        
        if final_count == len(sections):
            print(f"  ✅ SUCCESS - Section count matches file")
            return True
        else:
            print(f"  ⚠️  WARNING - Count mismatch (expected {len(sections)}, got {final_count})")
            return False
    
    def check_for_duplicates(self):
        """Check if any duplicates remain"""
        print("\n" + "="*80)
        print("CHECKING FOR REMAINING DUPLICATES")
        print("="*80)
        
        if self.use_async:
            result = self.execute("""
                SELECT chapter_id, section_number, COUNT(*) as count
                FROM sections
                WHERE chapter_id IN ('mn.3.1', 'sn.2.1', 'sn.4.1')
                GROUP BY chapter_id, section_number
                HAVING COUNT(*) > 1
            """)
            duplicates = result.rows if result.rows else []
        else:
            self.cursor.execute("""
                SELECT chapter_id, section_number, COUNT(*) as count
                FROM sections
                WHERE chapter_id IN ('mn.3.1', 'sn.2.1', 'sn.4.1')
                GROUP BY chapter_id, section_number
                HAVING COUNT(*) > 1
            """)
            duplicates = self.cursor.fetchall()
        
        if not duplicates:
            print("✅ No duplicates found!")
            return True
        else:
            print(f"❌ Still found {len(duplicates)} duplicates:")
            for dup in duplicates:
                chapter_id = dup[0] if isinstance(dup, (list, tuple)) else dup
                section_num = dup[1] if isinstance(dup, (list, tuple)) else None
                count = dup[2] if isinstance(dup, (list, tuple)) else None
                print(f"  - {chapter_id}, section {section_num}: {count} times")
            return False
    
    def close(self):
        """Close database connection"""
        if self.use_async:
            asyncio.run(self.client.close())
        else:
            self.conn.close()
        print("\n✓ Database connection closed")


def main():
    """Main function"""
    print("="*80)
    print("RECREATE CHAPTERS WITH DUPLICATE SECTIONS")
    print("="*80)
    
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        print("\n❌ Error: Environment variables not set!")
        sys.exit(1)
    
    try:
        recreator = ChapterRecreator(TURSO_DB_URL, TURSO_AUTH_TOKEN)
        
        # Step 1: Dry run
        print("\n" + "="*80)
        print("STEP 1: DRY RUN")
        print("="*80)
        
        for chapter_info in PROBLEM_CHAPTERS:
            recreator.recreate_chapter(chapter_info, dry_run=True)
        
        # Ask for confirmation
        print("\n" + "="*80)
        print("⚠️  WARNING: This will DELETE and RECREATE all sections for these 3 chapters!")
        print("="*80)
        response = input("\nProceed with recreation? (yes/no): ").strip().lower()
        
        if response != "yes":
            print("\n❌ Operation cancelled")
            recreator.close()
            return
        
        # Step 2: Actual recreation
        print("\n" + "="*80)
        print("STEP 2: RECREATING CHAPTERS")
        print("="*80)
        
        success_count = 0
        for chapter_info in PROBLEM_CHAPTERS:
            if recreator.recreate_chapter(chapter_info, dry_run=False):
                success_count += 1
        
        # Step 3: Verify no duplicates
        recreator.check_for_duplicates()
        
        # Summary
        print("\n" + "="*80)
        print("FINAL SUMMARY")
        print("="*80)
        print(f"Successfully recreated: {success_count}/{len(PROBLEM_CHAPTERS)} chapters")
        
        if success_count == len(PROBLEM_CHAPTERS):
            print("\n✅ All chapters recreated successfully!")
            print("\n📝 Next steps:")
            print("   1. Run: python check_sections_simple.py")
            print("   2. Verify no duplicates remain")
            print("   3. Add unique constraint: python add_unique_constraint.py")
        else:
            print("\n⚠️  Some chapters had issues. Please review the output above.")
        
        recreator.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
