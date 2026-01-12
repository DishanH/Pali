"""
Comprehensive Database Validation Script
Checks for missing translations, empty fields, and provides complete counts
"""

from import_to_turso_simple import TursoImporterSimple
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseValidator:
    def __init__(self, db_url, auth_token):
        self.client = TursoImporterSimple(db_url, auth_token).client
        
    def execute_query(self, query):
        """Execute query and return results in a clean format"""
        result = self.client.execute_query(query)
        if result.get('results') and result['results'][0].get('response', {}).get('result', {}).get('rows'):
            rows = result['results'][0]['response']['result']['rows']
            return [[cell['value'] if isinstance(cell, dict) else cell for cell in row] for row in rows]
        return []
    
    def get_basic_counts(self):
        """Get basic counts of all entities"""
        print("=" * 80)
        print("📊 BASIC DATABASE COUNTS")
        print("=" * 80)
        
        counts = {}
        
        # Basic counts
        queries = {
            'baskets': "SELECT COUNT(*) FROM baskets",
            'collections': "SELECT COUNT(*) FROM collections", 
            'books': "SELECT COUNT(*) FROM books",
            'chapters': "SELECT COUNT(*) FROM chapters",
            'sections': "SELECT COUNT(*) FROM sections"
        }
        
        for name, query in queries.items():
            result = self.execute_query(query)
            counts[name] = int(result[0][0]) if result else 0
            print(f"  {name.capitalize():12}: {counts[name]}")
        
        return counts
    
    def check_baskets(self):
        """Check baskets for missing translations"""
        print("\n" + "=" * 80)
        print("🧺 BASKETS VALIDATION")
        print("=" * 80)
        
        # Get all baskets
        baskets = self.execute_query("""
            SELECT id, name_pali, name_english, name_sinhala 
            FROM baskets
        """)
        
        print(f"Total Baskets: {len(baskets)}")
        
        issues = []
        for basket in baskets:
            basket_id, pali, english, sinhala = basket
            print(f"\n📦 Basket: {basket_id}")
            print(f"  Pali:    {pali or '❌ MISSING'}")
            print(f"  English: {english or '❌ MISSING'}")
            print(f"  Sinhala: {sinhala or '❌ MISSING'}")
            
            if not pali: issues.append(f"Basket {basket_id}: Missing Pali name")
            if not english: issues.append(f"Basket {basket_id}: Missing English name")
            if not sinhala: issues.append(f"Basket {basket_id}: Missing Sinhala name")
        
        if issues:
            print(f"\n⚠️  Found {len(issues)} basket issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ All baskets have complete translations!")
        
        return issues
    
    def check_collections(self):
        """Check collections for missing translations"""
        print("\n" + "=" * 80)
        print("📚 COLLECTIONS VALIDATION")
        print("=" * 80)
        
        collections = self.execute_query("""
            SELECT c.id, c.name_pali, c.name_english, c.name_sinhala, b.id as basket_id
            FROM collections c
            LEFT JOIN baskets b ON c.basket_id = b.id
            ORDER BY c.id
        """)
        
        print(f"Total Collections: {len(collections)}")
        
        issues = []
        for collection in collections:
            coll_id, pali, english, sinhala, basket_id = collection
            print(f"\n📖 Collection: {coll_id} (Basket: {basket_id})")
            print(f"  Pali:    {pali or '❌ MISSING'}")
            print(f"  English: {english or '❌ MISSING'}")
            print(f"  Sinhala: {sinhala or '❌ MISSING'}")
            
            if not pali: issues.append(f"Collection {coll_id}: Missing Pali name")
            if not english: issues.append(f"Collection {coll_id}: Missing English name")
            if not sinhala: issues.append(f"Collection {coll_id}: Missing Sinhala name")
            if not basket_id: issues.append(f"Collection {coll_id}: Missing basket reference")
        
        if issues:
            print(f"\n⚠️  Found {len(issues)} collection issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ All collections have complete translations!")
        
        return issues
    
    def check_books(self):
        """Check books for missing translations and metadata"""
        print("\n" + "=" * 80)
        print("📕 BOOKS VALIDATION")
        print("=" * 80)
        
        books = self.execute_query("""
            SELECT b.id, b.collection_id, b.book_type, b.name_pali, b.name_english, b.name_sinhala,
                   b.title_pali, b.title_english, b.title_sinhala,
                   b.footer_pali, b.footer_english, b.footer_sinhala,
                   b.total_chapters
            FROM books b
            ORDER BY b.collection_id, b.id
        """)
        
        print(f"Total Books: {len(books)}")
        
        issues = []
        for book in books:
            (book_id, coll_id, book_type, name_pali, name_english, name_sinhala,
             title_pali, title_english, title_sinhala,
             footer_pali, footer_english, footer_sinhala, total_chapters) = book
            
            print(f"\n📘 Book: {book_id} ({book_type}) - Collection: {coll_id}")
            print(f"  Name Pali:    {name_pali or '❌ MISSING'}")
            print(f"  Name English: {name_english or '❌ MISSING'}")
            print(f"  Name Sinhala: {name_sinhala or '❌ MISSING'}")
            print(f"  Title Pali:   {title_pali or '❌ MISSING'}")
            print(f"  Title English: {title_english or '❌ MISSING'}")
            print(f"  Title Sinhala: {title_sinhala or '❌ MISSING'}")
            print(f"  Footer Pali:   {footer_pali or '❌ MISSING'}")
            print(f"  Footer English: {footer_english or '❌ MISSING'}")
            print(f"  Footer Sinhala: {footer_sinhala or '❌ MISSING'}")
            print(f"  Total Chapters: {total_chapters}")
            
            # Check for missing fields
            if not name_pali: issues.append(f"Book {book_id}: Missing Pali name")
            if not name_english: issues.append(f"Book {book_id}: Missing English name")
            if not name_sinhala: issues.append(f"Book {book_id}: Missing Sinhala name")
            if not title_pali: issues.append(f"Book {book_id}: Missing Pali title")
            if not title_english: issues.append(f"Book {book_id}: Missing English title")
            if not title_sinhala: issues.append(f"Book {book_id}: Missing Sinhala title")
            if not footer_pali: issues.append(f"Book {book_id}: Missing Pali footer")
            if not footer_english: issues.append(f"Book {book_id}: Missing English footer")
            if not footer_sinhala: issues.append(f"Book {book_id}: Missing Sinhala footer")
        
        if issues:
            print(f"\n⚠️  Found {len(issues)} book issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ All books have complete translations!")
        
        return issues
    
    def check_chapters(self):
        """Check chapters for missing translations"""
        print("\n" + "=" * 80)
        print("📄 CHAPTERS VALIDATION")
        print("=" * 80)
        
        chapters = self.execute_query("""
            SELECT c.id, c.book_id, c.chapter_number, c.title_pali, c.title_english, c.title_sinhala
            FROM chapters c
            ORDER BY c.book_id, c.chapter_number
        """)
        
        print(f"Total Chapters: {len(chapters)}")
        
        issues = []
        missing_translations = {'pali': 0, 'english': 0, 'sinhala': 0}
        
        for chapter in chapters:
            chapter_id, book_id, chapter_num, title_pali, title_english, title_sinhala = chapter
            
            if not title_pali: 
                issues.append(f"Chapter {chapter_id} (Book: {book_id}): Missing Pali title")
                missing_translations['pali'] += 1
            if not title_english: 
                issues.append(f"Chapter {chapter_id} (Book: {book_id}): Missing English title")
                missing_translations['english'] += 1
            if not title_sinhala: 
                issues.append(f"Chapter {chapter_id} (Book: {book_id}): Missing Sinhala title")
                missing_translations['sinhala'] += 1
        
        print(f"\nChapter Translation Summary:")
        print(f"  Missing Pali titles:    {missing_translations['pali']}")
        print(f"  Missing English titles: {missing_translations['english']}")
        print(f"  Missing Sinhala titles: {missing_translations['sinhala']}")
        
        if issues:
            print(f"\n⚠️  Found {len(issues)} chapter issues")
            if len(issues) <= 20:  # Show first 20 issues
                for issue in issues:
                    print(f"  - {issue}")
            else:
                for issue in issues[:20]:
                    print(f"  - {issue}")
                print(f"  ... and {len(issues) - 20} more issues")
        else:
            print("\n✅ All chapters have complete translations!")
        
        return issues
    
    def check_sections(self):
        """Check sections for missing translations"""
        print("\n" + "=" * 80)
        print("📝 SECTIONS VALIDATION")
        print("=" * 80)
        
        # Get section counts by translation completeness
        section_stats = self.execute_query("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN pali IS NOT NULL AND pali != '' THEN 1 END) as has_pali,
                COUNT(CASE WHEN english IS NOT NULL AND english != '' THEN 1 END) as has_english,
                COUNT(CASE WHEN sinhala IS NOT NULL AND sinhala != '' THEN 1 END) as has_sinhala,
                COUNT(CASE WHEN pali_title IS NOT NULL AND pali_title != '' THEN 1 END) as has_pali_title,
                COUNT(CASE WHEN english_title IS NOT NULL AND english_title != '' THEN 1 END) as has_english_title,
                COUNT(CASE WHEN sinhala_title IS NOT NULL AND sinhala_title != '' THEN 1 END) as has_sinhala_title
            FROM sections
        """)
        
        if section_stats:
            total, has_pali, has_english, has_sinhala, has_pali_title, has_english_title, has_sinhala_title = section_stats[0]
            
            # Convert to integers
            total = int(total)
            has_pali = int(has_pali)
            has_english = int(has_english)
            has_sinhala = int(has_sinhala)
            has_pali_title = int(has_pali_title)
            has_english_title = int(has_english_title)
            has_sinhala_title = int(has_sinhala_title)
            
            print(f"Total Sections: {total}")
            print(f"\nContent Translation Coverage:")
            print(f"  Pali content:    {has_pali} / {total} ({has_pali/total*100:.1f}%)")
            print(f"  English content: {has_english} / {total} ({has_english/total*100:.1f}%)")
            print(f"  Sinhala content: {has_sinhala} / {total} ({has_sinhala/total*100:.1f}%)")
            
            print(f"\nTitle Translation Coverage:")
            print(f"  Pali titles:    {has_pali_title} / {total} ({has_pali_title/total*100:.1f}%)")
            print(f"  English titles: {has_english_title} / {total} ({has_english_title/total*100:.1f}%)")
            print(f"  Sinhala titles: {has_sinhala_title} / {total} ({has_sinhala_title/total*100:.1f}%)")
            
            # Find sections with missing content
            missing_content = self.execute_query("""
                SELECT chapter_id, section_number,
                       CASE WHEN pali IS NULL OR pali = '' THEN 'Missing Pali' ELSE NULL END as pali_issue,
                       CASE WHEN english IS NULL OR english = '' THEN 'Missing English' ELSE NULL END as english_issue,
                       CASE WHEN sinhala IS NULL OR sinhala = '' THEN 'Missing Sinhala' ELSE NULL END as sinhala_issue
                FROM sections
                WHERE (pali IS NULL OR pali = '') 
                   OR (english IS NULL OR english = '') 
                   OR (sinhala IS NULL OR sinhala = '')
                LIMIT 50
            """)
            
            issues = []
            if missing_content:
                print(f"\n⚠️  Found sections with missing content (showing first 50):")
                for row in missing_content:
                    chapter_id, section_num, pali_issue, english_issue, sinhala_issue = row
                    issues_list = [issue for issue in [pali_issue, english_issue, sinhala_issue] if issue]
                    if issues_list:
                        print(f"  - Chapter {chapter_id}, Section {section_num}: {', '.join(issues_list)}")
                        issues.extend(issues_list)
            
            return {
                'total': total,
                'coverage': {
                    'pali_content': has_pali/total*100,
                    'english_content': has_english/total*100,
                    'sinhala_content': has_sinhala/total*100,
                    'pali_titles': has_pali_title/total*100,
                    'english_titles': has_english_title/total*100,
                    'sinhala_titles': has_sinhala_title/total*100
                },
                'issues': issues
            }
        
        return {'total': 0, 'coverage': {}, 'issues': []}
    
    def check_data_consistency(self):
        """Check for data consistency issues"""
        print("\n" + "=" * 80)
        print("🔍 DATA CONSISTENCY CHECKS")
        print("=" * 80)
        
        issues = []
        
        # Check for orphaned records
        orphaned_books = self.execute_query("""
            SELECT b.id FROM books b 
            LEFT JOIN collections c ON b.collection_id = c.id 
            WHERE c.id IS NULL
        """)
        
        if orphaned_books:
            print(f"⚠️  Found {len(orphaned_books)} orphaned books (no collection):")
            for book in orphaned_books:
                print(f"  - Book ID: {book[0]}")
                issues.append(f"Orphaned book: {book[0]}")
        
        orphaned_chapters = self.execute_query("""
            SELECT c.id FROM chapters c 
            LEFT JOIN books b ON c.book_id = b.id 
            WHERE b.id IS NULL
        """)
        
        if orphaned_chapters:
            print(f"⚠️  Found {len(orphaned_chapters)} orphaned chapters (no book):")
            for chapter in orphaned_chapters:
                print(f"  - Chapter ID: {chapter[0]}")
                issues.append(f"Orphaned chapter: {chapter[0]}")
        
        orphaned_sections = self.execute_query("""
            SELECT s.chapter_id, COUNT(*) FROM sections s 
            LEFT JOIN chapters c ON s.chapter_id = c.id 
            WHERE c.id IS NULL
            GROUP BY s.chapter_id
        """)
        
        if orphaned_sections:
            print(f"⚠️  Found orphaned sections (no chapter):")
            for row in orphaned_sections:
                chapter_id, count = row
                print(f"  - Chapter ID {chapter_id}: {count} orphaned sections")
                issues.append(f"Orphaned sections in chapter: {chapter_id}")
        
        if not issues:
            print("✅ No data consistency issues found!")
        
        return issues
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE VALIDATION SUMMARY")
        print("=" * 80)
        
        # Run all validations
        basic_counts = self.get_basic_counts()
        basket_issues = self.check_baskets()
        collection_issues = self.check_collections()
        book_issues = self.check_books()
        chapter_issues = self.check_chapters()
        section_results = self.check_sections()
        consistency_issues = self.check_data_consistency()
        
        # Summary
        total_issues = (len(basket_issues) + len(collection_issues) + 
                       len(book_issues) + len(chapter_issues) + 
                       len(section_results.get('issues', [])) + len(consistency_issues))
        
        print(f"\n" + "=" * 80)
        print("🎯 FINAL VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Records: {sum(basic_counts.values())}")
        print(f"Total Issues Found: {total_issues}")
        
        if total_issues == 0:
            print("\n🎉 PERFECT! Your database is 100% complete and consistent!")
        else:
            print(f"\n⚠️  Issues breakdown:")
            print(f"  Basket issues: {len(basket_issues)}")
            print(f"  Collection issues: {len(collection_issues)}")
            print(f"  Book issues: {len(book_issues)}")
            print(f"  Chapter issues: {len(chapter_issues)}")
            print(f"  Section issues: {len(section_results.get('issues', []))}")
            print(f"  Consistency issues: {len(consistency_issues)}")
        
        # Translation coverage summary
        if 'coverage' in section_results:
            coverage = section_results['coverage']
            print(f"\n📊 Translation Coverage Summary:")
            print(f"  Average content coverage: {(coverage.get('pali_content', 0) + coverage.get('english_content', 0) + coverage.get('sinhala_content', 0))/3:.1f}%")
            print(f"  Average title coverage: {(coverage.get('pali_titles', 0) + coverage.get('english_titles', 0) + coverage.get('sinhala_titles', 0))/3:.1f}%")
        
        return {
            'total_records': sum(basic_counts.values()),
            'total_issues': total_issues,
            'basic_counts': basic_counts,
            'coverage': section_results.get('coverage', {}),
            'ready_for_production': total_issues == 0
        }

def main():
    print("=" * 80)
    print("🔍 COMPREHENSIVE DATABASE VALIDATION")
    print("   Checking for missing translations and data consistency")
    print("=" * 80)
    
    try:
        validator = DatabaseValidator(os.getenv('TURSO_DB_URL'), os.getenv('TURSO_AUTH_TOKEN'))
        summary = validator.generate_summary_report()
        
        print(f"\n" + "=" * 80)
        if summary['ready_for_production']:
            print("✅ DATABASE IS READY FOR PRODUCTION USE!")
        else:
            print("⚠️  DATABASE NEEDS ATTENTION BEFORE PRODUCTION USE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()