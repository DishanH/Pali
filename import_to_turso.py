"""
Import Pali Tipitaka JSON data to Turso database
This script imports data from the folder structure into Turso one folder at a time
"""

import json
import os
import sys
from pathlib import Path
import libsql_experimental as libsql

# Configuration
TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")  # e.g., "libsql://your-db.turso.io"
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")  # Your Turso auth token

# Nikaya folder mappings
NIKAYA_FOLDERS = {
    "Aṅguttaranikāyo": {
        "id": "anguttara",
        "name_pali": "Aṅguttara Nikāya",
        "name_english": "Numerical Discourses",
        "name_sinhala": "අංගුත්තර නිකාය"
    },
    "Dīghanikāyo": {
        "id": "digha",
        "name_pali": "Dīgha Nikāya",
        "name_english": "Long Discourses",
        "name_sinhala": "දීඝ නිකාය"
    },
    "Majjhimanikāye": {
        "id": "majjhima",
        "name_pali": "Majjhima Nikāya",
        "name_english": "Middle Length Discourses",
        "name_sinhala": "මජ්ඣිම නිකාය"
    },
    "Saṃyuttanikāyo": {
        "id": "samyutta",
        "name_pali": "Saṃyutta Nikāya",
        "name_english": "Connected Discourses",
        "name_sinhala": "සංයුත්ත නිකාය"
    }
}


class TursoImporter:
    def __init__(self, db_url, auth_token):
        """Initialize connection to Turso database"""
        if not db_url or not auth_token:
            raise ValueError("TURSO_DB_URL and TURSO_AUTH_TOKEN must be set")
        
        self.conn = libsql.connect(database=db_url, auth_token=auth_token)
        self.cursor = self.conn.cursor()
        print("✓ Connected to Turso database")
    
    def initialize_schema(self):
        """Create tables if they don't exist"""
        print("\n📋 Initializing database schema...")
        with open("turso_schema.sql", "r", encoding="utf-8") as f:
            schema = f.read()
        
        # Execute each statement separately
        statements = [s.strip() for s in schema.split(';') if s.strip()]
        for statement in statements:
            try:
                self.cursor.execute(statement)
            except Exception as e:
                print(f"Warning: {e}")
        
        self.conn.commit()
        print("✓ Schema initialized")
    
    def insert_nikaya(self, nikaya_data):
        """Insert or update a nikaya"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO nikayas (id, name_pali, name_english, name_sinhala)
            VALUES (?, ?, ?, ?)
        """, (
            nikaya_data["id"],
            nikaya_data["name_pali"],
            nikaya_data["name_english"],
            nikaya_data["name_sinhala"]
        ))
    
    def insert_book(self, book_data, nikaya_id):
        """Insert or update a book"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO books (
                id, nikaya_id, name, title_pali, title_english, title_sinhala,
                footer_pali, footer_english, footer_sinhala,
                description_english, description_sinhala,
                total_chapters, version, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            book_data.get("id", book_data.get("name")),
            nikaya_id,
            book_data.get("name", ""),
            book_data.get("title", {}).get("pali", ""),
            book_data.get("title", {}).get("english", ""),
            book_data.get("title", {}).get("sinhala", ""),
            book_data.get("footer", {}).get("pali", "") if isinstance(book_data.get("footer"), dict) else book_data.get("footer", ""),
            book_data.get("footer", {}).get("english", "") if isinstance(book_data.get("footer"), dict) else "",
            book_data.get("footer", {}).get("sinhala", "") if isinstance(book_data.get("footer"), dict) else "",
            book_data.get("description", {}).get("english", ""),
            book_data.get("description", {}).get("sinhala", ""),
            book_data.get("totalChapters", len(book_data.get("chapters", []))),
            book_data.get("version", ""),
            book_data.get("lastUpdated", "")
        ))
    
    def insert_chapter_metadata(self, chapter_data, book_id):
        """Insert or update chapter metadata from book.json"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO chapters (
                id, book_id, chapter_number, title_pali, title_english, title_sinhala,
                description_english, description_sinhala, link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chapter_data.get("id"),
            book_id,
            chapter_data.get("number"),
            chapter_data.get("title", {}).get("pali", ""),
            chapter_data.get("title", {}).get("english", ""),
            chapter_data.get("title", {}).get("sinhala", ""),
            chapter_data.get("description", {}).get("english", ""),
            chapter_data.get("description", {}).get("sinhala", ""),
            chapter_data.get("link", "")
        ))
    
    def insert_sections(self, chapter_id, sections):
        """Insert sections (suttas) for a chapter"""
        for section in sections:
            self.cursor.execute("""
                INSERT INTO sections (
                    chapter_id, section_number, pali, english, sinhala,
                    pali_title, english_title, sinhala_title,
                    vagga, vagga_english, vagga_sinhala
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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
            ))
    
    def import_book_folder(self, nikaya_folder, book_folder):
        """Import a single book folder (e.g., Mahāvaggo)"""
        nikaya_path = Path(nikaya_folder)
        book_path = nikaya_path / book_folder
        
        if not book_path.exists():
            print(f"❌ Folder not found: {book_path}")
            return False
        
        # Skip pdf folders
        if book_folder.lower() == "pdfs":
            print(f"⏭️  Skipping PDF folder: {book_folder}")
            return True
        
        print(f"\n📚 Importing: {nikaya_folder} > {book_folder}")
        
        # Get nikaya info
        nikaya_info = NIKAYA_FOLDERS.get(nikaya_folder)
        if not nikaya_info:
            print(f"❌ Unknown nikaya: {nikaya_folder}")
            return False
        
        # Insert nikaya if not exists
        self.insert_nikaya(nikaya_info)
        
        # Read book.json
        book_json_path = book_path / "book.json"
        if not book_json_path.exists():
            print(f"❌ book.json not found in {book_path}")
            return False
        
        with open(book_json_path, "r", encoding="utf-8") as f:
            book_data = json.load(f)
        
        # Insert book
        book_id = book_data.get("id", book_data.get("name"))
        self.insert_book(book_data, nikaya_info["id"])
        print(f"  ✓ Book metadata inserted: {book_id}")
        
        # Insert chapter metadata from book.json
        chapters = book_data.get("chapters", [])
        for chapter_meta in chapters:
            self.insert_chapter_metadata(chapter_meta, book_id)
        print(f"  ✓ {len(chapters)} chapter metadata entries inserted")
        
        # Import chapter content files
        chapters_folder = book_path / "chapters"
        if not chapters_folder.exists():
            print(f"  ⚠️  No chapters folder found")
            self.conn.commit()
            return True
        
        chapter_files = list(chapters_folder.glob("*.json"))
        sections_count = 0
        
        for chapter_file in chapter_files:
            with open(chapter_file, "r", encoding="utf-8") as f:
                chapter_data = json.load(f)
            
            chapter_id = chapter_data.get("id")
            sections = chapter_data.get("sections", [])
            
            if sections:
                self.insert_sections(chapter_id, sections)
                sections_count += len(sections)
        
        print(f"  ✓ {len(chapter_files)} chapter files processed")
        print(f"  ✓ {sections_count} sections inserted")
        
        self.conn.commit()
        print(f"✅ Successfully imported {book_folder}")
        return True
    
    def import_nikaya(self, nikaya_folder):
        """Import all books in a nikaya"""
        nikaya_path = Path(nikaya_folder)
        
        if not nikaya_path.exists():
            print(f"❌ Nikaya folder not found: {nikaya_folder}")
            return False
        
        # Get all book folders
        book_folders = [f.name for f in nikaya_path.iterdir() if f.is_dir() and f.name.lower() != "pdfs"]
        
        print(f"\n{'='*60}")
        print(f"📖 Importing Nikaya: {nikaya_folder}")
        print(f"   Found {len(book_folders)} book folders")
        print(f"{'='*60}")
        
        success_count = 0
        for book_folder in book_folders:
            try:
                if self.import_book_folder(nikaya_folder, book_folder):
                    success_count += 1
            except Exception as e:
                print(f"❌ Error importing {book_folder}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print(f"✅ Nikaya import complete: {success_count}/{len(book_folders)} books imported")
        print(f"{'='*60}\n")
        
        return success_count == len(book_folders)
    
    def get_stats(self):
        """Get database statistics"""
        stats = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM nikayas")
        stats["nikayas"] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM books")
        stats["books"] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM chapters")
        stats["chapters"] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM sections")
        stats["sections"] = self.cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("\n✓ Database connection closed")


def main():
    """Main import function"""
    print("=" * 60)
    print("Pali Tipitaka Turso Database Importer")
    print("=" * 60)
    
    # Check environment variables
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        print("\n❌ Error: Environment variables not set!")
        print("\nPlease set:")
        print("  TURSO_DB_URL=your_database_url")
        print("  TURSO_AUTH_TOKEN=your_auth_token")
        print("\nExample:")
        print('  set TURSO_DB_URL=libsql://your-db.turso.io')
        print('  set TURSO_AUTH_TOKEN=your_token_here')
        sys.exit(1)
    
    try:
        # Initialize importer
        importer = TursoImporter(TURSO_DB_URL, TURSO_AUTH_TOKEN)
        
        # Initialize schema
        importer.initialize_schema()
        
        # Interactive mode
        print("\n" + "=" * 60)
        print("Import Options:")
        print("=" * 60)
        print("1. Import single book folder")
        print("2. Import entire Nikaya")
        print("3. Import all Nikayas")
        print("4. Show database statistics")
        print("5. Exit")
        print("=" * 60)
        
        while True:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\nAvailable Nikayas:")
                for i, nikaya in enumerate(NIKAYA_FOLDERS.keys(), 1):
                    print(f"  {i}. {nikaya}")
                
                nikaya_choice = input("\nSelect Nikaya (1-4): ").strip()
                nikaya_list = list(NIKAYA_FOLDERS.keys())
                
                if nikaya_choice.isdigit() and 1 <= int(nikaya_choice) <= len(nikaya_list):
                    nikaya_folder = nikaya_list[int(nikaya_choice) - 1]
                    nikaya_path = Path(nikaya_folder)
                    
                    if nikaya_path.exists():
                        book_folders = [f.name for f in nikaya_path.iterdir() 
                                      if f.is_dir() and f.name.lower() != "pdfs"]
                        
                        print(f"\nAvailable books in {nikaya_folder}:")
                        for i, book in enumerate(book_folders, 1):
                            print(f"  {i}. {book}")
                        
                        book_choice = input(f"\nSelect book (1-{len(book_folders)}): ").strip()
                        
                        if book_choice.isdigit() and 1 <= int(book_choice) <= len(book_folders):
                            book_folder = book_folders[int(book_choice) - 1]
                            importer.import_book_folder(nikaya_folder, book_folder)
                        else:
                            print("❌ Invalid book selection")
                    else:
                        print(f"❌ Nikaya folder not found: {nikaya_folder}")
                else:
                    print("❌ Invalid nikaya selection")
            
            elif choice == "2":
                print("\nAvailable Nikayas:")
                for i, nikaya in enumerate(NIKAYA_FOLDERS.keys(), 1):
                    print(f"  {i}. {nikaya}")
                
                nikaya_choice = input("\nSelect Nikaya (1-4): ").strip()
                nikaya_list = list(NIKAYA_FOLDERS.keys())
                
                if nikaya_choice.isdigit() and 1 <= int(nikaya_choice) <= len(nikaya_list):
                    nikaya_folder = nikaya_list[int(nikaya_choice) - 1]
                    importer.import_nikaya(nikaya_folder)
                else:
                    print("❌ Invalid selection")
            
            elif choice == "3":
                confirm = input("\n⚠️  This will import ALL data. Continue? (yes/no): ").strip().lower()
                if confirm == "yes":
                    for nikaya_folder in NIKAYA_FOLDERS.keys():
                        importer.import_nikaya(nikaya_folder)
                else:
                    print("❌ Import cancelled")
            
            elif choice == "4":
                stats = importer.get_stats()
                print("\n" + "=" * 60)
                print("Database Statistics:")
                print("=" * 60)
                print(f"  Nikayas:  {stats['nikayas']}")
                print(f"  Books:    {stats['books']}")
                print(f"  Chapters: {stats['chapters']}")
                print(f"  Sections: {stats['sections']}")
                print("=" * 60)
            
            elif choice == "5":
                print("\n👋 Exiting...")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-5.")
        
        # Close connection
        importer.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
