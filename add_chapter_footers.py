"""
Add missing chapter footer columns and import all chapter footers
"""

from import_to_turso_simple import TursoImporterSimple
from dotenv import load_dotenv
import os
import json
from pathlib import Path

load_dotenv()

class ChapterFooterUpdater:
    def __init__(self, db_url, auth_token):
        self.client = TursoImporterSimple(db_url, auth_token).client
        
    def add_footer_columns(self):
        """Add footer columns to chapters table"""
        print("🔧 Adding footer columns to chapters table...")
        
        try:
            # Add footer columns
            self.client.execute_query("ALTER TABLE chapters ADD COLUMN footer_pali TEXT")
            print("✅ Added footer_pali column")
        except Exception as e:
            print(f"⚠️  footer_pali column might already exist: {e}")
        
        try:
            self.client.execute_query("ALTER TABLE chapters ADD COLUMN footer_english TEXT")
            print("✅ Added footer_english column")
        except Exception as e:
            print(f"⚠️  footer_english column might already exist: {e}")
        
        try:
            self.client.execute_query("ALTER TABLE chapters ADD COLUMN footer_sinhala TEXT")
            print("✅ Added footer_sinhala column")
        except Exception as e:
            print(f"⚠️  footer_sinhala column might already exist: {e}")
    
    def update_chapter_footer(self, chapter_id, footer_data):
        """Update a single chapter with footer data"""
        self.client.execute_query("""
            UPDATE chapters 
            SET footer_pali = ?, footer_english = ?, footer_sinhala = ?
            WHERE id = ?
        """, [
            footer_data.get("pali", ""),
            footer_data.get("english", ""),
            footer_data.get("sinhala", ""),
            chapter_id
        ])
    
    def import_all_chapter_footers(self):
        """Import footers from all chapter files"""
        print("\n📚 Importing chapter footers from all collections...")
        
        collections = ["Saṃyuttanikāyo", "Majjhimanikāye", "Dīghanikāyo", "Aṅguttaranikāyo"]
        
        total_updated = 0
        total_missing = 0
        
        for collection in collections:
            print(f"\n📖 Processing {collection}...")
            collection_path = Path(collection)
            
            if not collection_path.exists():
                print(f"❌ Collection folder not found: {collection}")
                continue
            
            # Get all book folders
            book_folders = [f for f in collection_path.iterdir() if f.is_dir() and f.name.lower() != "pdfs"]
            
            for book_folder in book_folders:
                print(f"  📘 Processing book: {book_folder.name}")
                
                chapters_folder = book_folder / "chapters"
                if not chapters_folder.exists():
                    print(f"    ⚠️  No chapters folder in {book_folder.name}")
                    continue
                
                # Process all chapter files
                chapter_files = list(chapters_folder.glob("*.json"))
                
                for chapter_file in chapter_files:
                    try:
                        with open(chapter_file, 'r', encoding='utf-8') as f:
                            chapter_data = json.load(f)
                        
                        chapter_id = chapter_data.get("id")
                        footer = chapter_data.get("footer")
                        
                        if footer and chapter_id:
                            self.update_chapter_footer(chapter_id, footer)
                            total_updated += 1
                            print(f"    ✅ Updated footer for {chapter_id}")
                        else:
                            total_missing += 1
                            print(f"    ⚠️  No footer found in {chapter_file.name}")
                            
                    except Exception as e:
                        print(f"    ❌ Error processing {chapter_file.name}: {e}")
                        total_missing += 1
        
        print(f"\n📊 Footer Import Summary:")
        print(f"  ✅ Updated: {total_updated} chapters")
        print(f"  ⚠️  Missing: {total_missing} chapters")
        
        return total_updated, total_missing
    
    def verify_footers(self):
        """Verify that footers were imported correctly"""
        print("\n🔍 Verifying imported footers...")
        
        # Count chapters with footers
        result = self.client.execute_query("""
            SELECT COUNT(*) FROM chapters 
            WHERE footer_pali IS NOT NULL AND footer_pali != ''
        """)
        
        count_with_footers = int(result['results'][0]['response']['result']['rows'][0][0]['value'])
        
        # Total chapters
        result = self.client.execute_query("SELECT COUNT(*) FROM chapters")
        total_chapters = int(result['results'][0]['response']['result']['rows'][0][0]['value'])
        
        print(f"📊 Verification Results:")
        print(f"  Total chapters: {total_chapters}")
        print(f"  Chapters with footers: {count_with_footers}")
        print(f"  Coverage: {count_with_footers/total_chapters*100:.1f}%")
        
        # Show sample footers
        result = self.client.execute_query("""
            SELECT id, footer_pali, footer_english, footer_sinhala 
            FROM chapters 
            WHERE footer_pali IS NOT NULL AND footer_pali != ''
            LIMIT 3
        """)
        
        if result['results'][0]['response']['result']['rows']:
            print(f"\n📄 Sample footers:")
            rows = result['results'][0]['response']['result']['rows']
            for row in rows:
                chapter_id = row[0]['value']
                footer_pali = row[1]['value']
                footer_english = row[2]['value']
                footer_sinhala = row[3]['value']
                
                print(f"  Chapter {chapter_id}:")
                print(f"    Pali: {footer_pali[:100]}...")
                print(f"    English: {footer_english[:100]}...")
                print(f"    Sinhala: {footer_sinhala[:100]}...")

def main():
    print("=" * 80)
    print("🔧 ADDING CHAPTER FOOTERS TO DATABASE")
    print("=" * 80)
    
    try:
        updater = ChapterFooterUpdater(os.getenv('TURSO_DB_URL'), os.getenv('TURSO_AUTH_TOKEN'))
        
        # Step 1: Add footer columns
        updater.add_footer_columns()
        
        # Step 2: Import all chapter footers
        total_updated, total_missing = updater.import_all_chapter_footers()
        
        # Step 3: Verify results
        updater.verify_footers()
        
        print("\n" + "=" * 80)
        if total_updated > 0:
            print("🎉 SUCCESS! Chapter footers have been added to the database!")
        else:
            print("⚠️  No footers were imported - please check for issues")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()