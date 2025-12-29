"""
Updated Import Pali Tipitaka JSON data to Turso database
This script imports data from the updated standardized book.json structure
"""

import json
import os
import sys
from pathlib import Path
import libsql_experimental as libsql

# Configuration
TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")  # e.g., "libsql://your-db.turso.io"
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")  # Your Turso auth token

# Collection folder mappings
COLLECTION_FOLDERS = {
    "Aṅguttaranikāyo": "anguttaranikaya",
    "Dīghanikāyo": "dighanikaya", 
    "Majjhimanikāye": "majjhimanikaya",
    "Saṃyuttanikāyo": "samyuttanikaya"
}


class TursoImporterUpdated:
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
    
    def insert_basket(self, basket_data):
        """Insert or update a basket"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO baskets (id, name_pali, name_english, name_sinhala)
            VALUES (?, ?, ?, ?)
        """, (
            basket_data["id"],
            basket_data["name"]["pali"],
            basket_data["name"]["english"],
            basket_data["name"]["sinhala"]
        ))
    
    def insert_collection(self, collection_data, basket_id):
        """Insert or update a collection"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO collections (id, basket_id, name_pali, name_english, name_sinhala)
            VALUES (?, ?, ?, ?, ?)
        """, (
            collection_data["id"],
            basket_id,
            collection_data["name"]["pali"],
            collection_data["name"]["english"],
            collection_data["name"]["sinhala"]
        ))
    
    def insert_book(self, book_data):
        """Insert or update a book with the new standardized structure"""
        # Determine book type and get the appropriate subdivision data
        book_type = None
        subdivision_data = None
        book_number = None
        
        if "vagga" in book_data:
            book_type = "vagga"
            subdivision_data = book_data["vagga"]
            book_number = subdivision_data.get("number")
        elif "nipata" in book_data:
            book_type = "nipata"
            subdivision_data = book_data["nipata"]
            book_number = subdivision_data.get("number")
        elif "pannasa" in book_data:
            book_type = "pannasa"
            subdivision_data = book_data["pannasa"]
            book_number = subdivision_data.get("number")
        
        # Convert language translations array to JSON string
        language_translations = json.dumps(book_data.get("language", {}).get("translations", []))
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO books (
                id, collection_id, book_type, book_number, book_id_pali,
                name_pali, name_english, name_sinhala,
                title_pali, title_english, title_sinhala,
                footer_pali, footer_english, footer_sinhala,
                description_english, description_sinhala,
                total_chapters, language_source, language_translations,
                version, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            book_data["id"],
            book_data["collection"]["id"],
            book_type,
            book_number,
            subdivision_data["id"] if subdivision_data else book_data["id"],
            subdivision_data["name"]["pali"] if subdivision_data else book_data["title"]["pali"],
            subdivision_data["name"]["english"] if subdivision_data else book_data["title"]["english"],
            subdivision_data["name"]["sinhala"] if subdivision_data else book_data["title"]["sinhala"],
            book_data["title"]["pali"],
            book_data["title"]["english"],
            book_data["title"]["sinhala"],
            book_data["footer"]["pali"],
            book_data["footer"]["english"],
            book_data["footer"]["sinhala"],
            book_data.get("description", {}).get("english", ""),
            book_data.get("description", {}).get("sinhala", ""),
            book_data.get("totalChapters", len(book_data.get("chapters", []))),
            book_data.get("language", {}).get("source", "pali"),
            language_translations,
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
    
    def import_book_metadata_only(self, collection_folder, book_folder):
        """Import only book.json metadata (books and chapter metadata, no content)"""
        collection_path = Path(collection_folder)
        book_path = collection_path / book_folder
        
        if not book_path.exists():
            print(f"❌ Folder not found: {book_path}")
            return False
        
        # Skip pdf folders
        if book_folder.lower() == "pdfs":
            print(f"⏭️  Skipping PDF folder: {book_folder}")
            return True
        
        print(f"\n📚 Importing book metadata: {collection_folder} > {book_folder}")
        
        # Read book.json
        book_json_path = book_path / "book.json"
        if not book_json_path.exists():
            print(f"❌ book.json not found in {book_path}")
            return False
        
        with open(book_json_path, "r", encoding="utf-8") as f:
            book_data = json.load(f)
        
        # Insert basket if not exists
        if "basket" in book_data:
            self.insert_basket(book_data["basket"])
        
        # Insert collection if not exists
        if "collection" in book_data:
            basket_id = book_data.get("basket", {}).get("id", "sutta")
            self.insert_collection(book_data["collection"], basket_id)
        
        # Insert book
        book_id = book_data["id"]
        self.insert_book(book_data)
        print(f"  ✓ Book metadata inserted: {book_id}")
        
        # Insert chapter metadata from book.json
        chapters = book_data.get("chapters", [])
        for chapter_meta in chapters:
            self.insert_chapter_metadata(chapter_meta, book_id)
        print(f"  ✓ {len(chapters)} chapter metadata entries inserted")
        
        self.conn.commit()
        print(f"✅ Book metadata imported: {book_folder}")
        return True
    
    def import_book_chapters_only(self, collection_folder, book_folder):
        """Import only chapter content files (sections/suttas)"""
        collection_path = Path(collection_folder)
        book_path = collection_path / book_folder
        
        if not book_path.exists():
            print(f"❌ Folder not found: {book_path}")
            return False
        
        # Skip pdf folders
        if book_folder.lower() == "pdfs":
            print(f"⏭️  Skipping PDF folder: {book_folder}")
            return True
        
        print(f"\n📖 Importing chapter content: {collection_folder} > {book_folder}")
        
        # Read book.json to get book_id
        book_json_path = book_path / "book.json"
        if not book_json_path.exists():
            print(f"❌ book.json not found in {book_path}")
            return False
        
        with open(book_json_path, "r", encoding="utf-8") as f:
            book_data = json.load(f)
        
        book_id = book_data["id"]
        
        # Import chapter content files
        chapters_folder = book_path / "chapters"
        if not chapters_folder.exists():
            print(f"  ⚠️  No chapters folder found")
            return True
        
        chapter_files = list(chapters_folder.glob("*.json"))
        sections_count = 0
        
        for chapter_file in chapter_files:
            try:
                with open(chapter_file, "r", encoding="utf-8") as f:
                    chapter_data = json.load(f)
                
                chapter_id = chapter_data.get("id")
                sections = chapter_data.get("sections", [])
                
                if sections:
                    self.insert_sections(chapter_id, sections)
                    sections_count += len(sections)
                    print(f"  ✓ {chapter_file.name}: {len(sections)} sections")
            except Exception as e:
                print(f"  ⚠️  Error processing {chapter_file.name}: {e}")
        
        print(f"  ✓ {len(chapter_files)} chapter files processed")
        print(f"  ✓ {sections_count} total sections inserted")
        
        self.conn.commit()
        print(f"✅ Chapter content imported: {book_folder}")
        return True
    
    def import_book_folder(self, collection_folder, book_folder):
        """Import a single book folder with updated structure (both metadata and content)"""
        print(f"\n📚 Full import: {collection_folder} > {book_folder}")
        
        # Import metadata first
        metadata_success = self.import_book_metadata_only(collection_folder, book_folder)
        if not metadata_success:
            return False
        
        # Then import chapter content
        content_success = self.import_book_chapters_only(collection_folder, book_folder)
        
        return metadata_success and content_success
    
    def import_collection_metadata_only(self, collection_folder):
        """Import all book metadata in a collection (no chapter content)"""
        collection_path = Path(collection_folder)
        
        if not collection_path.exists():
            print(f"❌ Collection folder not found: {collection_folder}")
            return False
        
        # Get all book folders
        book_folders = [f.name for f in collection_path.iterdir() if f.is_dir() and f.name.lower() != "pdfs"]
        
        print(f"\n{'='*60}")
        print(f"📖 Importing Collection Metadata: {collection_folder}")
        print(f"   Found {len(book_folders)} book folders")
        print(f"{'='*60}")
        
        success_count = 0
        for book_folder in book_folders:
            try:
                if self.import_book_metadata_only(collection_folder, book_folder):
                    success_count += 1
            except Exception as e:
                print(f"❌ Error importing metadata for {book_folder}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print(f"✅ Collection metadata import complete: {success_count}/{len(book_folders)} books")
        print(f"{'='*60}\n")
        
        return success_count == len(book_folders)
    
    def import_collection_chapters_only(self, collection_folder):
        """Import all chapter content in a collection (assumes metadata already imported)"""
        collection_path = Path(collection_folder)
        
        if not collection_path.exists():
            print(f"❌ Collection folder not found: {collection_folder}")
            return False
        
        # Get all book folders
        book_folders = [f.name for f in collection_path.iterdir() if f.is_dir() and f.name.lower() != "pdfs"]
        
        print(f"\n{'='*60}")
        print(f"📚 Importing Collection Chapters: {collection_folder}")
        print(f"   Found {len(book_folders)} book folders")
        print(f"{'='*60}")
        
        success_count = 0
        total_sections = 0
        
        for book_folder in book_folders:
            try:
                if self.import_book_chapters_only(collection_folder, book_folder):
                    success_count += 1
                    # Get section count for this book
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM sections s
                        JOIN chapters c ON s.chapter_id = c.id
                        JOIN books b ON c.book_id = b.id
                        WHERE b.collection_id = (
                            SELECT collection_id FROM books 
                            WHERE id = (
                                SELECT id FROM books 
                                WHERE collection_id IN (
                                    SELECT id FROM collections 
                                    WHERE name_pali LIKE ?
                                )
                                LIMIT 1
                            )
                        )
                    """, (f"%{collection_folder.split('/')[-1]}%",))
                    
            except Exception as e:
                print(f"❌ Error importing chapters for {book_folder}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print(f"✅ Collection chapters import complete: {success_count}/{len(book_folders)} books")
        print(f"{'='*60}\n")
        
        return success_count == len(book_folders)
    
    def import_collection(self, collection_folder):
        """Import all books in a collection (both metadata and content)"""
        print(f"\n{'='*60}")
        print(f"📖 Full Collection Import: {collection_folder}")
        print(f"{'='*60}")
        
        # Phase 1: Import all book metadata
        print(f"\n🔄 Phase 1: Importing book metadata...")
        metadata_success = self.import_collection_metadata_only(collection_folder)
        
        if not metadata_success:
            print(f"❌ Metadata import failed for {collection_folder}")
            return False
        
        # Phase 2: Import all chapter content
        print(f"\n🔄 Phase 2: Importing chapter content...")
        content_success = self.import_collection_chapters_only(collection_folder)
        
        success = metadata_success and content_success
        
        print(f"\n{'='*60}")
        if success:
            print(f"✅ Full collection import complete: {collection_folder}")
        else:
            print(f"❌ Collection import had issues: {collection_folder}")
        print(f"{'='*60}\n")
        
        return success
    
    def get_stats(self):
        """Get database statistics"""
        stats = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM baskets")
        stats["baskets"] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM collections")
        stats["collections"] = self.cursor.fetchone()[0]
        
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
    print("Pali Tipitaka Turso Database Importer (Updated)")
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
        importer = TursoImporterUpdated(TURSO_DB_URL, TURSO_AUTH_TOKEN)
        
        # Initialize schema
        importer.initialize_schema()
        
        # Interactive mode
        print("\n" + "=" * 60)
        print("Import Options:")
        print("=" * 60)
        print("1. Import single book (full)")
        print("2. Import single book metadata only")
        print("3. Import single book chapters only")
        print("4. Import collection (full)")
        print("5. Import collection metadata only")
        print("6. Import collection chapters only")
        print("7. Import all collections (full)")
        print("8. Show database statistics")
        print("9. Exit")
        print("=" * 60)
        
        while True:
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == "1":
                # Import single book (full)
                print("\nAvailable Collections:")
                for i, collection in enumerate(COLLECTION_FOLDERS.keys(), 1):
                    print(f"  {i}. {collection}")
                
                collection_choice = input("\nSelect Collection (1-4): ").strip()
                collection_list = list(COLLECTION_FOLDERS.keys())
                
                if collection_choice.isdigit() and 1 <= int(collection_choice) <= len(collection_list):
                    collection_folder = collection_list[int(collection_choice) - 1]
                    collection_path = Path(collection_folder)
                    
                    if collection_path.exists():
                        book_folders = [f.name for f in collection_path.iterdir() 
                                      if f.is_dir() and f.name.lower() != "pdfs"]
                        
                        print(f"\nAvailable books in {collection_folder}:")
                        for i, book in enumerate(book_folders, 1):
                            print(f"  {i}. {book}")
                        
                        book_choice = input(f"\nSelect book (1-{len(book_folders)}): ").strip()
                        
                        if book_choice.isdigit() and 1 <= int(book_choice) <= len(book_folders):
                            book_folder = book_folders[int(book_choice) - 1]
                            importer.import_book_folder(collection_folder, book_folder)
                        else:
                            print("❌ Invalid book selection")
                    else:
                        print(f"❌ Collection folder not found: {collection_folder}")
                else:
                    print("❌ Invalid collection selection")
            
            elif choice == "2":
                # Import single book metadata only
                print("\nAvailable Collections:")
                for i, collection in enumerate(COLLECTION_FOLDERS.keys(), 1):
                    print(f"  {i}. {collection}")
                
                collection_choice = input("\nSelect Collection (1-4): ").strip()
                collection_list = list(COLLECTION_FOLDERS.keys())
                
                if collection_choice.isdigit() and 1 <= int(collection_choice) <= len(collection_list):
                    collection_folder = collection_list[int(collection_choice) - 1]
                    collection_path = Path(collection_folder)
                    
                    if collection_path.exists():
                        book_folders = [f.name for f in collection_path.iterdir() 
                                      if f.is_dir() and f.name.lower() != "pdfs"]
                        
                        print(f"\nAvailable books in {collection_folder}:")
                        for i, book in enumerate(book_folders, 1):
                            print(f"  {i}. {book}")
                        
                        book_choice = input(f"\nSelect book (1-{len(book_folders)}): ").strip()
                        
                        if book_choice.isdigit() and 1 <= int(book_choice) <= len(book_folders):
                            book_folder = book_folders[int(book_choice) - 1]
                            importer.import_book_metadata_only(collection_folder, book_folder)
                        else:
                            print("❌ Invalid book selection")
                    else:
                        print(f"❌ Collection folder not found: {collection_folder}")
                else:
                    print("❌ Invalid collection selection")
            
            elif choice == "3":
                # Import single book chapters only
                print("\nAvailable Collections:")
                for i, collection in enumerate(COLLECTION_FOLDERS.keys(), 1):
                    print(f"  {i}. {collection}")
                
                collection_choice = input("\nSelect Collection (1-4): ").strip()
                collection_list = list(COLLECTION_FOLDERS.keys())
                
                if collection_choice.isdigit() and 1 <= int(collection_choice) <= len(collection_list):
                    collection_folder = collection_list[int(collection_choice) - 1]
                    collection_path = Path(collection_folder)
                    
                    if collection_path.exists():
                        book_folders = [f.name for f in collection_path.iterdir() 
                                      if f.is_dir() and f.name.lower() != "pdfs"]
                        
                        print(f"\nAvailable books in {collection_folder}:")
                        for i, book in enumerate(book_folders, 1):
                            print(f"  {i}. {book}")
                        
                        book_choice = input(f"\nSelect book (1-{len(book_folders)}): ").strip()
                        
                        if book_choice.isdigit() and 1 <= int(book_choice) <= len(book_folders):
                            book_folder = book_folders[int(book_choice) - 1]
                            importer.import_book_chapters_only(collection_folder, book_folder)
                        else:
                            print("❌ Invalid book selection")
                    else:
                        print(f"❌ Collection folder not found: {collection_folder}")
                else:
                    print("❌ Invalid collection selection")
            
            elif choice == "4":
                # Import collection (full)
                print("\nAvailable Collections:")
                for i, collection in enumerate(COLLECTION_FOLDERS.keys(), 1):
                    print(f"  {i}. {collection}")
                
                collection_choice = input("\nSelect Collection (1-4): ").strip()
                collection_list = list(COLLECTION_FOLDERS.keys())
                
                if collection_choice.isdigit() and 1 <= int(collection_choice) <= len(collection_list):
                    collection_folder = collection_list[int(collection_choice) - 1]
                    importer.import_collection(collection_folder)
                else:
                    print("❌ Invalid selection")
            
            elif choice == "5":
                # Import collection metadata only
                print("\nAvailable Collections:")
                for i, collection in enumerate(COLLECTION_FOLDERS.keys(), 1):
                    print(f"  {i}. {collection}")
                
                collection_choice = input("\nSelect Collection (1-4): ").strip()
                collection_list = list(COLLECTION_FOLDERS.keys())
                
                if collection_choice.isdigit() and 1 <= int(collection_choice) <= len(collection_list):
                    collection_folder = collection_list[int(collection_choice) - 1]
                    importer.import_collection_metadata_only(collection_folder)
                else:
                    print("❌ Invalid selection")
            
            elif choice == "6":
                # Import collection chapters only
                print("\nAvailable Collections:")
                for i, collection in enumerate(COLLECTION_FOLDERS.keys(), 1):
                    print(f"  {i}. {collection}")
                
                collection_choice = input("\nSelect Collection (1-4): ").strip()
                collection_list = list(COLLECTION_FOLDERS.keys())
                
                if collection_choice.isdigit() and 1 <= int(collection_choice) <= len(collection_list):
                    collection_folder = collection_list[int(collection_choice) - 1]
                    importer.import_collection_chapters_only(collection_folder)
                else:
                    print("❌ Invalid selection")
            
            elif choice == "7":
                # Import all collections (full)
                confirm = input("\n⚠️  This will import ALL data. Continue? (yes/no): ").strip().lower()
                if confirm == "yes":
                    for collection_folder in COLLECTION_FOLDERS.keys():
                        importer.import_collection(collection_folder)
                else:
                    print("❌ Import cancelled")
            
            elif choice == "8":
                # Show database statistics
                stats = importer.get_stats()
                print("\n" + "=" * 60)
                print("Database Statistics:")
                print("=" * 60)
                print(f"  Baskets:     {stats['baskets']}")
                print(f"  Collections: {stats['collections']}")
                print(f"  Books:       {stats['books']}")
                print(f"  Chapters:    {stats['chapters']}")
                print(f"  Sections:    {stats['sections']}")
                print("=" * 60)
            
            elif choice == "9":
                # Exit
                print("\n👋 Exiting...")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-9.")
        
        # Close connection
        importer.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()