"""
Check for missing chapter footers in the database
"""

from import_to_turso_simple import TursoImporterSimple
from dotenv import load_dotenv
import os
import json
from pathlib import Path

load_dotenv()

class FooterChecker:
    def __init__(self, db_url, auth_token):
        self.client = TursoImporterSimple(db_url, auth_token).client
        
    def execute_query(self, query):
        """Execute query and return results in a clean format"""
        result = self.client.execute_query(query)
        if result.get('results') and result['results'][0].get('response', {}).get('result', {}).get('rows'):
            rows = result['results'][0]['response']['result']['rows']
            return [[cell['value'] if isinstance(cell, dict) else cell for cell in row] for row in rows]
        return []
    
    def check_database_schema(self):
        """Check if chapters table has footer columns"""
        print("🔍 Checking database schema for footer columns...")
        
        # Check if footer columns exist
        schema_query = """
            PRAGMA table_info(chapters)
        """
        
        columns = self.execute_query(schema_query)
        column_names = [col[1] for col in columns]  # Column name is at index 1
        
        print(f"Current chapters table columns: {column_names}")
        
        footer_columns = ['footer_pali', 'footer_english', 'footer_sinhala']
        missing_columns = [col for col in footer_columns if col not in column_names]
        
        if missing_columns:
            print(f"❌ Missing footer columns: {missing_columns}")
            return False
        else:
            print("✅ All footer columns exist in database")
            return True
    
    def check_sample_chapter_files(self):
        """Check sample chapter files to see footer structure"""
        print("\n🔍 Checking sample chapter files for footer structure...")
        
        collections = ["Saṃyuttanikāyo", "Majjhimanikāye", "Dīghanikāyo", "Aṅguttaranikāyo"]
        
        for collection in collections:
            collection_path = Path(collection)
            if collection_path.exists():
                # Get first book folder
                book_folders = [f for f in collection_path.iterdir() if f.is_dir() and f.name.lower() != "pdfs"]
                if book_folders:
                    first_book = book_folders[0]
                    chapters_folder = first_book / "chapters"
                    if chapters_folder.exists():
                        # Get first chapter file
                        chapter_files = list(chapters_folder.glob("*.json"))
                        if chapter_files:
                            first_chapter = chapter_files[0]
                            print(f"\n📄 Sample: {first_chapter}")
                            
                            with open(first_chapter, 'r', encoding='utf-8') as f:
                                chapter_data = json.load(f)
                            
                            print(f"  Has footer: {'footer' in chapter_data}")
                            if 'footer' in chapter_data:
                                footer = chapter_data['footer']
                                print(f"  Footer Pali: {footer.get('pali', 'MISSING')}")
                                print(f"  Footer English: {footer.get('english', 'MISSING')}")
                                print(f"  Footer Sinhala: {footer.get('sinhala', 'MISSING')}")
                            break
                break
    
    def count_chapters_with_footers(self):
        """Count how many chapters in database have footers"""
        print("\n📊 Checking database for existing chapter footers...")
        
        # Check if footer columns exist first
        if not self.check_database_schema():
            print("❌ Cannot check footers - columns don't exist")
            return
        
        total_chapters = self.execute_query("SELECT COUNT(*) FROM chapters")[0][0]
        
        chapters_with_footers = self.execute_query("""
            SELECT COUNT(*) FROM chapters 
            WHERE footer_pali IS NOT NULL AND footer_pali != ''
        """)[0][0]
        
        print(f"Total chapters: {total_chapters}")
        print(f"Chapters with footers: {chapters_with_footers}")
        print(f"Missing footers: {int(total_chapters) - int(chapters_with_footers)}")
        
        if int(chapters_with_footers) == 0:
            print("❌ NO CHAPTER FOOTERS FOUND IN DATABASE!")
        else:
            print(f"✅ Found {chapters_with_footers} chapters with footers")

def main():
    print("=" * 80)
    print("🔍 CHECKING FOR MISSING CHAPTER FOOTERS")
    print("=" * 80)
    
    try:
        checker = FooterChecker(os.getenv('TURSO_DB_URL'), os.getenv('TURSO_AUTH_TOKEN'))
        
        # Check sample files
        checker.check_sample_chapter_files()
        
        # Check database
        checker.count_chapters_with_footers()
        
        print("\n" + "=" * 80)
        print("🎯 CONCLUSION: We need to add chapter footers to the database!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()