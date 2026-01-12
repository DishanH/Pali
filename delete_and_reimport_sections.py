"""
Delete and reimport specific sections with updated vagga and titles
Targets: mn.3.1-Devadahavaggo, sn.4.1-Saḷāyatanasaṃyuttaṃ, sn.2.1-Nidānasaṃyuttaṃ
"""

import json
import os
import sys
from pathlib import Path
from turso_python import TursoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

# Chapter files to reimport
CHAPTERS_TO_REIMPORT = [
    {
        "id": "mn.3.1",
        "path": "Majjhimanikāye/Uparipaṇṇāsapāḷi/chapters/mn.3.1-Devadahavaggo.json"
    },
    {
        "id": "sn.4.1",
        "path": "Saṃyuttanikāyo/Saḷāyatanavaggo/chapters/sn.4.1-Saḷāyatanasaṃyuttaṃ.json"
    },
    {
        "id": "sn.2.1",
        "path": "Saṃyuttanikāyo/Nidānavaggo/chapters/sn.2.1-Nidānasaṃyuttaṃ.json"
    }
]


class SectionReimporter:
    def __init__(self, db_url, auth_token):
        """Initialize connection to Turso database"""
        if not db_url or not auth_token:
            raise ValueError("TURSO_DB_URL and TURSO_AUTH_TOKEN must be set")
        
        self.client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✓ Connected to Turso database")
    
    def delete_sections_for_chapter(self, chapter_id):
        """Delete all sections for a specific chapter"""
        print(f"\n🗑️  Deleting sections for chapter: {chapter_id}")
        
        # First, check how many sections exist
        result = self.client.execute_query(
            "SELECT COUNT(*) FROM sections WHERE chapter_id = ?",
            [chapter_id]
        )
        rows = result['results'][0]['response']['result']['rows']
        count = rows[0][0]['value']
        
        if count == 0:
            print(f"  ⚠️  No sections found for {chapter_id}")
            return False
        
        print(f"  Found {count} sections to delete")
        
        # Delete the sections
        self.client.execute_query(
            "DELETE FROM sections WHERE chapter_id = ?",
            [chapter_id]
        )
        
        print(f"  ✓ Deleted {count} sections")
        return True
    
    def insert_sections(self, chapter_id, sections):
        """Insert sections (suttas) for a chapter"""
        inserted_count = 0
        for section in sections:
            try:
                self.client.execute_query("""
                    INSERT INTO sections (
                        chapter_id, section_number, pali, english, sinhala,
                        pali_title, english_title, sinhala_title,
                        vagga, vagga_english, vagga_sinhala
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
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
                ])
                inserted_count += 1
            except Exception as e:
                print(f"  ⚠️  Error inserting section {section.get('number')}: {e}")
        
        return inserted_count
    
    def reimport_chapter(self, chapter_info):
        """Delete and reimport a single chapter's sections"""
        chapter_id = chapter_info["id"]
        chapter_path = Path(chapter_info["path"])
        
        print(f"\n{'='*60}")
        print(f"📖 Processing: {chapter_id}")
        print(f"   File: {chapter_path}")
        print(f"{'='*60}")
        
        # Check if file exists
        if not chapter_path.exists():
            print(f"❌ File not found: {chapter_path}")
            return False
        
        # Load chapter data
        try:
            with open(chapter_path, "r", encoding="utf-8") as f:
                chapter_data = json.load(f)
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
        
        # Verify chapter ID matches
        if chapter_data.get("id") != chapter_id:
            print(f"⚠️  Warning: File ID ({chapter_data.get('id')}) doesn't match expected ID ({chapter_id})")
        
        # Delete existing sections
        self.delete_sections_for_chapter(chapter_id)
        
        # Insert new sections
        sections = chapter_data.get("sections", [])
        if not sections:
            print(f"  ⚠️  No sections found in file")
            return False
        
        print(f"\n📝 Inserting {len(sections)} sections...")
        inserted_count = self.insert_sections(chapter_id, sections)
        
        print(f"  ✓ Successfully inserted {inserted_count}/{len(sections)} sections")
        
        # Verify the reimport
        result = self.client.execute_query(
            "SELECT COUNT(*) FROM sections WHERE chapter_id = ?",
            [chapter_id]
        )
        rows = result['results'][0]['response']['result']['rows']
        final_count = rows[0][0]['value']
        
        print(f"  ✓ Verification: {final_count} sections now in database")
        
        # Show sample of vagga data
        result = self.client.execute_query("""
            SELECT section_number, vagga, vagga_english, vagga_sinhala
            FROM sections 
            WHERE chapter_id = ? 
            ORDER BY section_number 
            LIMIT 3
        """, [chapter_id])
        
        rows = result['results'][0]['response']['result']['rows']
        if rows:
            print(f"\n  📋 Sample vagga data:")
            for row in rows:
                section_num = row[0]['value']
                vagga = row[1]['value'] if row[1]['value'] else ""
                vagga_en = row[2]['value'] if row[2]['value'] else ""
                vagga_si = row[3]['value'] if row[3]['value'] else ""
                print(f"     Section {section_num}: {vagga} | {vagga_en} | {vagga_si}")
        
        return True
    
    def reimport_all(self):
        """Reimport all specified chapters"""
        print("\n" + "="*60)
        print("🔄 SECTION REIMPORT PROCESS")
        print("="*60)
        print(f"Chapters to process: {len(CHAPTERS_TO_REIMPORT)}")
        
        success_count = 0
        for chapter_info in CHAPTERS_TO_REIMPORT:
            try:
                if self.reimport_chapter(chapter_info):
                    success_count += 1
            except Exception as e:
                print(f"\n❌ Error processing {chapter_info['id']}: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*60)
        print(f"✅ REIMPORT COMPLETE: {success_count}/{len(CHAPTERS_TO_REIMPORT)} chapters")
        print("="*60)
        
        return success_count == len(CHAPTERS_TO_REIMPORT)
    
    def close(self):
        """Close database connection"""
        # turso_python doesn't need explicit close
        print("\n✓ Database connection closed")


def main():
    """Main function"""
    print("=" * 60)
    print("Delete and Reimport Sections with Updated Vagga/Titles")
    print("=" * 60)
    
    # Check environment variables
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        print("\n❌ Error: Environment variables not set!")
        print("\nPlease set:")
        print("  TURSO_DB_URL=your_database_url")
        print("  TURSO_AUTH_TOKEN=your_auth_token")
        sys.exit(1)
    
    try:
        # Initialize reimporter
        reimporter = SectionReimporter(TURSO_DB_URL, TURSO_AUTH_TOKEN)
        
        # Confirm action
        print("\n⚠️  This will DELETE and REIMPORT sections for:")
        for chapter in CHAPTERS_TO_REIMPORT:
            print(f"   - {chapter['id']}")
        
        confirm = input("\nContinue? (yes/no): ").strip().lower()
        
        if confirm != "yes":
            print("❌ Operation cancelled")
            sys.exit(0)
        
        # Perform reimport
        success = reimporter.reimport_all()
        
        # Close connection
        reimporter.close()
        
        if success:
            print("\n✅ All sections successfully reimported!")
            sys.exit(0)
        else:
            print("\n⚠️  Some chapters had issues. Please review the output above.")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
