"""
Import Pali Tipitaka JSON data to Turso database (Fixed version)
This script imports data from the updated standardized book.json structure
Uses libsql-client instead of libsql_experimental
"""

import json
import os
import sys
from pathlib import Path
import asyncio
from libsql_client import create_client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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


class TursoImporterFixed:
    def __init__(self, db_url, auth_token):
        """Initialize connection to Turso database"""
        if not db_url or not auth_token:
            raise ValueError("TURSO_DB_URL and TURSO_AUTH_TOKEN must be set")
        
        self.client = create_client(url=db_url, auth_token=auth_token)
        print("✓ Connected to Turso database")
    
    async def initialize_schema(self):
        """Create tables if they don't exist"""
        print("\n📋 Initializing database schema...")
        with open("turso_schema.sql", "r", encoding="utf-8") as f:
            schema = f.read()
        
        # Execute each statement separately
        statements = [s.strip() for s in schema.split(';') if s.strip()]
        for statement in statements:
            try:
                await self.client.execute(statement)
            except Exception as e:
                print(f"Warning: {e}")
        
        print("✓ Schema initialized")
    
    async def insert_basket(self, basket_data):
        """Insert or update a basket"""
        await self.client.execute("""
            INSERT OR REPLACE INTO baskets (id, name_pali, name_english, name_sinhala)
            VALUES (?, ?, ?, ?)
        """, [
            basket_data["id"],
            basket_data["name"]["pali"],
            basket_data["name"]["english"],
            basket_data["name"]["sinhala"]
        ])
    
    async def insert_collection(self, collection_data, basket_id):
        """Insert or update a collection"""
        await self.client.execute("""
            INSERT OR REPLACE INTO collections (id, basket_id, name_pali, name_english, name_sinhala)
            VALUES (?, ?, ?, ?, ?)
        """, [
            collection_data["id"],
            basket_id,
            collection_data["name"]["pali"],
            collection_data["name"]["english"],
            collection_data["name"]["sinhala"]
        ])
    
    async def insert_book(self, book_data):
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
        
        await self.client.execute("""
            INSERT OR REPLACE INTO books (
                id, collection_id, book_type, book_number, book_id_pali,
                name_pali, name_english, name_sinhala,
                title_pali, title_english, title_sinhala,
                footer_pali, footer_english, footer_sinhala,
                description_english, description_sinhala,
                total_chapters, language_source, language_translations,
                version, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
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
        ])
    
    async def insert_chapter_metadata(self, chapter_data, book_id):
        """Insert or update chapter metadata from book.json"""
        await self.client.execute("""
            INSERT OR REPLACE INTO chapters (
                id, book_id, chapter_number, title_pali, title_english, title_sinhala,
                description_english, description_sinhala, link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            chapter_data.get("id"),
            book_id,
            chapter_data.get("number"),
            chapter_data.get("title", {}).get("pali", ""),
            chapter_data.get("title", {}).get("english", ""),
            chapter_data.get("title", {}).get("sinhala", ""),
            chapter_data.get("description", {}).get("english", ""),
            chapter_data.get("description", {}).get("sinhala", ""),
            chapter_data.get("link", "")
        ])
    
    async def insert_sections(self, chapter_id, sections):
        """Insert sections (suttas) for a chapter"""
        for section in sections:
            await self.client.execute("""
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
    
    async def import_collection(self, collection_folder):
        """Import all books in a collection (both metadata and content)"""
        collection_path = Path(collection_folder)
        
        if not collection_path.exists():
            print(f"❌ Collection folder not found: {collection_folder}")
            return False
        
        # Get all book folders
        book_folders = [f.name for f in collection_path.iterdir() if f.is_dir() and f.name.lower() != "pdfs"]
        
        print(f"\n{'='*60}")
        print(f"📖 Full Collection Import: {collection_folder}")
        print(f"   Found {len(book_folders)} book folders")
        print(f"{'='*60}")
        
        success_count = 0
        total_sections = 0
        
        for book_folder in book_folders:
            try:
                book_path = collection_path / book_folder
                
                # Skip pdf folders
                if book_folder.lower() == "pdfs":
                    print(f"⏭️  Skipping PDF folder: {book_folder}")
                    continue
                
                print(f"\n📚 Importing: {collection_folder} > {book_folder}")
                
                # Read book.json
                book_json_path = book_path / "book.json"
                if not book_json_path.exists():
                    print(f"❌ book.json not found in {book_path}")
                    continue
                
                with open(book_json_path, "r", encoding="utf-8") as f:
                    book_data = json.load(f)
                
                # Insert basket if not exists
                if "basket" in book_data:
                    await self.insert_basket(book_data["basket"])
                
                # Insert collection if not exists
                if "collection" in book_data:
                    basket_id = book_data.get("basket", {}).get("id", "sutta")
                    await self.insert_collection(book_data["collection"], basket_id)
                
                # Insert book
                book_id = book_data["id"]
                await self.insert_book(book_data)
                print(f"  ✓ Book metadata inserted: {book_id}")
                
                # Insert chapter metadata from book.json
                chapters = book_data.get("chapters", [])
                for chapter_meta in chapters:
                    await self.insert_chapter_metadata(chapter_meta, book_id)
                print(f"  ✓ {len(chapters)} chapter metadata entries inserted")
                
                # Import chapter content files
                chapters_folder = book_path / "chapters"
                if not chapters_folder.exists():
                    print(f"  ⚠️  No chapters folder found")
                    success_count += 1
                    continue
                
                chapter_files = list(chapters_folder.glob("*.json"))
                sections_count = 0
                
                for chapter_file in chapter_files:
                    try:
                        with open(chapter_file, "r", encoding="utf-8") as f:
                            chapter_data = json.load(f)
                        
                        chapter_id = chapter_data.get("id")
                        sections = chapter_data.get("sections", [])
                        
                        if sections:
                            await self.insert_sections(chapter_id, sections)
                            sections_count += len(sections)
                            print(f"  ✓ {chapter_file.name}: {len(sections)} sections")
                    except Exception as e:
                        print(f"  ⚠️  Error processing {chapter_file.name}: {e}")
                
                print(f"  ✓ {len(chapter_files)} chapter files processed")
                print(f"  ✓ {sections_count} sections inserted")
                total_sections += sections_count
                
                print(f"✅ Successfully imported {book_folder}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Error importing {book_folder}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print(f"✅ Collection import complete: {success_count}/{len(book_folders)} books")
        print(f"   Total sections imported: {total_sections}")
        print(f"{'='*60}\n")
        
        return success_count == len(book_folders)
    
    async def get_stats(self):
        """Get database statistics"""
        stats = {}
        
        result = await self.client.execute("SELECT COUNT(*) FROM baskets")
        stats["baskets"] = result.rows[0][0] if result.rows else 0
        
        result = await self.client.execute("SELECT COUNT(*) FROM collections")
        stats["collections"] = result.rows[0][0] if result.rows else 0
        
        result = await self.client.execute("SELECT COUNT(*) FROM books")
        stats["books"] = result.rows[0][0] if result.rows else 0
        
        result = await self.client.execute("SELECT COUNT(*) FROM chapters")
        stats["chapters"] = result.rows[0][0] if result.rows else 0
        
        result = await self.client.execute("SELECT COUNT(*) FROM sections")
        stats["sections"] = result.rows[0][0] if result.rows else 0
        
        return stats
    
    async def close(self):
        """Close database connection"""
        await self.client.close()
        print("\n✓ Database connection closed")


async def main():
    """Main import function"""
    print("=" * 60)
    print("Pali Tipitaka Turso Database Importer (Fixed)")
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
        importer = TursoImporterFixed(TURSO_DB_URL, TURSO_AUTH_TOKEN)
        
        # Initialize schema
        await importer.initialize_schema()
        
        # Import Saṃyuttanikāyo collection
        print("\n🚀 Starting Saṃyuttanikāyo import...")
        success = await importer.import_collection("Saṃyuttanikāyo")
        
        if success:
            print("\n🎉 Import completed successfully!")
        else:
            print("\n⚠️  Import completed with some issues")
        
        # Show final statistics
        stats = await importer.get_stats()
        print("\n" + "=" * 60)
        print("Final Database Statistics:")
        print("=" * 60)
        print(f"  Baskets:     {stats['baskets']}")
        print(f"  Collections: {stats['collections']}")
        print(f"  Books:       {stats['books']}")
        print(f"  Chapters:    {stats['chapters']}")
        print(f"  Sections:    {stats['sections']}")
        print("=" * 60)
        
        # Close connection
        await importer.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())