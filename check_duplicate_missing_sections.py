"""
Check for duplicate and missing sections in Turso database
This script identifies:
1. Duplicate section entries (same chapter_id + section_number)
2. Missing sections (gaps in section numbering)
3. Sections with duplicate content
"""

import os
import sys
from pathlib import Path
import json
from collections import defaultdict
from dotenv import load_dotenv

# Try to import database library
try:
    import libsql_experimental as libsql
    DB_LIB = "libsql_experimental"
except ImportError:
    try:
        from libsql_client import create_client
        DB_LIB = "libsql_client"
    except ImportError:
        print("❌ No Turso database library found!")
        print("Please install one of:")
        print("  pip install libsql-experimental")
        print("  pip install libsql-client")
        sys.exit(1)

# Load environment variables
load_dotenv()

# Configuration
TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

# Collection folders to check against
COLLECTION_FOLDERS = [
    "Aṅguttaranikāyo",
    "Dīghanikāyo",
    "Majjhimanikāye",
    "Saṃyuttanikāyo"
]


class SectionChecker:
    def __init__(self, db_url, auth_token):
        """Initialize connection to Turso database"""
        if not db_url or not auth_token:
            raise ValueError("TURSO_DB_URL and TURSO_AUTH_TOKEN must be set")
        
        if DB_LIB == "libsql_experimental":
            self.conn = libsql.connect(database=db_url, auth_token=auth_token)
            self.cursor = self.conn.cursor()
            self.is_async = False
        else:  # libsql_client
            self.client = create_client(url=db_url, auth_token=auth_token)
            self.is_async = True
        
        print(f"✓ Connected to Turso database (using {DB_LIB})")
    
    def execute_query(self, query, params=None):
        """Execute query based on library type"""
        if self.is_async:
            import asyncio
            return asyncio.run(self._execute_async(query, params))
        else:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
    
    async def _execute_async(self, query, params=None):
        """Execute async query for libsql_client"""
        if params:
            result = await self.client.execute(query, params)
        else:
            result = await self.client.execute(query)
        return result.rows if hasattr(result, 'rows') else []
    
    def check_duplicate_sections(self):
        """Find duplicate sections (same chapter_id + section_number)"""
        print("\n" + "="*80)
        print("CHECKING FOR DUPLICATE SECTIONS")
        print("="*80)
        
        # Find duplicates by chapter_id and section_number
        duplicates = self.execute_query("""
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
        
        if not duplicates:
            print("✅ No duplicate sections found!")
            return []
        
        print(f"\n⚠️  Found {len(duplicates)} duplicate section entries:\n")
        
        duplicate_details = []
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
            
            # Get details of each duplicate
            ids = section_ids.split(',')
            section_details = []
            
            for sid in ids:
                self.cursor.execute("""
                    SELECT id, pali_title, english_title, sinhala_title, 
                           LENGTH(pali) as pali_len, LENGTH(english) as eng_len, 
                           LENGTH(sinhala) as sin_len
                    FROM sections
                    WHERE id = ?
                """, (int(sid),))
                
                section_info = self.cursor.fetchone()
                if section_info:
                    section_details.append(section_info)
            
            duplicate_details.append({
                'chapter_id': chapter_id,
                'section_number': section_num,
                'count': count,
                'collection': collection_name,
                'book': book_name,
                'chapter_pali': chapter_title_pali,
                'chapter_english': chapter_title_eng,
                'section_ids': ids,
                'section_details': section_details
            })
            
            print(f"Chapter: {chapter_id}")
            print(f"  Collection: {collection_name}")
            print(f"  Book: {book_name}")
            print(f"  Chapter: {chapter_title_pali} ({chapter_title_eng})")
            print(f"  Section Number: {section_num}")
            print(f"  Duplicate Count: {count}")
            print(f"  Section IDs: {section_ids}")
            
            for detail in section_details:
                sid, pali_title, eng_title, sin_title, pali_len, eng_len, sin_len = detail
                print(f"    - ID {sid}:")
                print(f"      Pali Title: {pali_title}")
                print(f"      English Title: {eng_title}")
                print(f"      Content lengths: Pali={pali_len}, Eng={eng_len}, Sin={sin_len}")
            print()
        
        return duplicate_details
    
    def check_missing_sections(self):
        """Find missing sections (gaps in section numbering)"""
        print("\n" + "="*80)
        print("CHECKING FOR MISSING SECTIONS")
        print("="*80)
        
        # Get all chapters
        self.cursor.execute("""
            SELECT c.id, c.title_pali, c.title_english, b.name_pali, col.name_pali
            FROM chapters c
            JOIN books b ON c.book_id = b.id
            JOIN collections col ON b.collection_id = col.id
            ORDER BY col.name_pali, b.name_pali, c.chapter_number
        """)
        
        chapters = self.cursor.fetchall()
        
        missing_sections = []
        total_gaps = 0
        
        for chapter_id, chapter_pali, chapter_eng, book_name, collection_name in chapters:
            # Get all section numbers for this chapter
            self.cursor.execute("""
                SELECT DISTINCT section_number
                FROM sections
                WHERE chapter_id = ?
                ORDER BY section_number
            """, (chapter_id,))
            
            section_numbers = [row[0] for row in self.cursor.fetchall()]
            
            if not section_numbers:
                continue
            
            # Check for gaps
            min_num = min(section_numbers)
            max_num = max(section_numbers)
            expected_numbers = set(range(min_num, max_num + 1))
            actual_numbers = set(section_numbers)
            missing = sorted(expected_numbers - actual_numbers)
            
            if missing:
                total_gaps += len(missing)
                missing_sections.append({
                    'chapter_id': chapter_id,
                    'collection': collection_name,
                    'book': book_name,
                    'chapter_pali': chapter_pali,
                    'chapter_english': chapter_eng,
                    'missing_numbers': missing,
                    'range': f"{min_num}-{max_num}",
                    'total_sections': len(section_numbers)
                })
        
        if not missing_sections:
            print("✅ No missing sections found!")
            return []
        
        print(f"\n⚠️  Found {total_gaps} missing sections across {len(missing_sections)} chapters:\n")
        
        for item in missing_sections:
            print(f"Chapter: {item['chapter_id']}")
            print(f"  Collection: {item['collection']}")
            print(f"  Book: {item['book']}")
            print(f"  Chapter: {item['chapter_pali']} ({item['chapter_english']})")
            print(f"  Section Range: {item['range']}")
            print(f"  Total Sections: {item['total_sections']}")
            print(f"  Missing Numbers: {item['missing_numbers']}")
            print()
        
        return missing_sections
    
    def check_file_vs_database(self):
        """Compare JSON files with database to find discrepancies"""
        print("\n" + "="*80)
        print("COMPARING FILES WITH DATABASE")
        print("="*80)
        
        discrepancies = []
        
        for collection_folder in COLLECTION_FOLDERS:
            collection_path = Path(collection_folder)
            
            if not collection_path.exists():
                print(f"⏭️  Skipping {collection_folder} (folder not found)")
                continue
            
            print(f"\n📂 Checking {collection_folder}...")
            
            # Get all book folders
            book_folders = [f for f in collection_path.iterdir() 
                          if f.is_dir() and f.name.lower() != "pdfs"]
            
            for book_folder in book_folders:
                chapters_folder = book_folder / "chapters"
                
                if not chapters_folder.exists():
                    continue
                
                # Check each chapter file
                chapter_files = list(chapters_folder.glob("*.json"))
                
                for chapter_file in chapter_files:
                    try:
                        with open(chapter_file, "r", encoding="utf-8") as f:
                            chapter_data = json.load(f)
                        
                        chapter_id = chapter_data.get("id")
                        file_sections = chapter_data.get("sections", [])
                        
                        # Get sections from database
                        self.cursor.execute("""
                            SELECT section_number, id
                            FROM sections
                            WHERE chapter_id = ?
                            ORDER BY section_number
                        """, (chapter_id,))
                        
                        db_sections = self.cursor.fetchall()
                        
                        file_count = len(file_sections)
                        db_count = len(db_sections)
                        
                        if file_count != db_count:
                            discrepancies.append({
                                'chapter_id': chapter_id,
                                'file_path': str(chapter_file),
                                'file_count': file_count,
                                'db_count': db_count,
                                'difference': db_count - file_count
                            })
                            
                            print(f"  ⚠️  {chapter_file.name}")
                            print(f"      File sections: {file_count}")
                            print(f"      DB sections: {db_count}")
                            print(f"      Difference: {db_count - file_count}")
                    
                    except Exception as e:
                        print(f"  ❌ Error reading {chapter_file.name}: {e}")
        
        if not discrepancies:
            print("\n✅ All files match database!")
        else:
            print(f"\n⚠️  Found {len(discrepancies)} files with mismatched section counts")
        
        return discrepancies
    
    def generate_report(self, duplicates, missing, discrepancies):
        """Generate a comprehensive report"""
        report_path = "section_check_report.json"
        
        report = {
            "summary": {
                "duplicate_entries": len(duplicates),
                "chapters_with_missing_sections": len(missing),
                "total_missing_sections": sum(len(m['missing_numbers']) for m in missing),
                "file_db_mismatches": len(discrepancies)
            },
            "duplicates": duplicates,
            "missing_sections": missing,
            "file_db_discrepancies": discrepancies
        }
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Duplicate section entries: {report['summary']['duplicate_entries']}")
        print(f"Chapters with missing sections: {report['summary']['chapters_with_missing_sections']}")
        print(f"Total missing sections: {report['summary']['total_missing_sections']}")
        print(f"File/DB mismatches: {report['summary']['file_db_mismatches']}")
        print(f"\n📄 Detailed report saved to: {report_path}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("\n✓ Database connection closed")


def main():
    """Main function"""
    print("="*80)
    print("SECTION DUPLICATE AND MISSING CHECK")
    print("="*80)
    
    # Check environment variables
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        print("\n❌ Error: Environment variables not set!")
        print("\nPlease set:")
        print("  TURSO_DB_URL=your_database_url")
        print("  TURSO_AUTH_TOKEN=your_auth_token")
        sys.exit(1)
    
    try:
        # Initialize checker
        checker = SectionChecker(TURSO_DB_URL, TURSO_AUTH_TOKEN)
        
        # Run checks
        duplicates = checker.check_duplicate_sections()
        missing = checker.check_missing_sections()
        discrepancies = checker.check_file_vs_database()
        
        # Generate report
        checker.generate_report(duplicates, missing, discrepancies)
        
        # Close connection
        checker.close()
        
        print("\n✅ Check complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
