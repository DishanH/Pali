#!/usr/bin/env python3
"""
Extract Book Translations Script
Extracts all book.json files, clears English/Sinhala translations,
and creates a folder with clean JSON files for manual translation.
"""

import json
from pathlib import Path
import shutil

class BookTranslationExtractor:
    def __init__(self):
        self.output_folder = Path("book_translations_for_manual_work")
        self.collections = [
            "Dīghanikāyo",
            "Majjhimanikāye", 
            "Saṃyuttanikāyo",
            "Aṅguttaranikāyo"
        ]
        self.processed_files = []
    
    def clear_translations(self, obj):
        """Recursively clear English and Sinhala translations from an object"""
        if isinstance(obj, dict):
            # Clear English and Sinhala fields
            if 'english' in obj:
                obj['english'] = ""
            if 'sinhala' in obj:
                obj['sinhala'] = ""
            
            # Clear description and summary fields that might have bad translations
            if 'description' in obj:
                if isinstance(obj['description'], dict):
                    if 'english' in obj['description']:
                        obj['description']['english'] = ""
                    if 'sinhala' in obj['description']:
                        obj['description']['sinhala'] = ""
                elif isinstance(obj['description'], str):
                    obj['description'] = ""
            
            if 'summary' in obj:
                if isinstance(obj['summary'], dict):
                    if 'english' in obj['summary']:
                        obj['summary']['english'] = ""
                    if 'sinhala' in obj['summary']:
                        obj['summary']['sinhala'] = ""
                elif isinstance(obj['summary'], str):
                    obj['summary'] = ""
            
            # Recursively process nested objects
            for key, value in obj.items():
                self.clear_translations(value)
        
        elif isinstance(obj, list):
            # Process each item in the list
            for item in obj:
                self.clear_translations(item)
    
    def process_book_file(self, book_path, collection_name, book_name):
        """Process a single book.json file"""
        try:
            # Read the original file
            with open(book_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            # Clear all English and Sinhala translations
            self.clear_translations(book_data)
            
            # Create output directory structure
            collection_dir = self.output_folder / collection_name
            collection_dir.mkdir(parents=True, exist_ok=True)
            
            # Save the cleaned file
            output_file = collection_dir / f"{book_name}_book.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
            
            # Track the file for reference
            self.processed_files.append({
                "original_path": str(book_path),
                "output_path": str(output_file),
                "collection": collection_name,
                "book": book_name
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing {book_path}: {e}")
            return False
    
    def scan_collection(self, collection_name):
        """Scan all books in a collection"""
        collection_path = Path(collection_name)
        
        if not collection_path.exists():
            print(f"⚠️  Collection not found: {collection_name}")
            return
        
        print(f"📚 Processing {collection_name}...")
        
        # Get all book folders
        book_folders = [f for f in collection_path.iterdir() 
                       if f.is_dir() and f.name.lower() != "pdfs"]
        
        processed_count = 0
        
        for book_folder in book_folders:
            book_json_path = book_folder / "book.json"
            if book_json_path.exists():
                if self.process_book_file(book_json_path, collection_name, book_folder.name):
                    processed_count += 1
                    print(f"  ✓ {book_folder.name}")
        
        print(f"  📊 {collection_name}: {processed_count} books processed")
    
    def create_reference_file(self):
        """Create a reference file mapping output files to original locations"""
        reference_data = {
            "metadata": {
                "created_date": "2025-12-29",
                "purpose": "Reference mapping for book translation files",
                "instructions": {
                    "workflow": [
                        "1. Translate the JSON files in the book_translations_for_manual_work folder",
                        "2. Use apply_book_translations.py to copy translations back to original files",
                        "3. Verify with extract_missing_translations.py"
                    ],
                    "translation_fields": [
                        "Fill in all 'english' and 'sinhala' fields",
                        "Translate 'description' and 'summary' fields if present",
                        "Keep 'pali' fields unchanged"
                    ]
                }
            },
            "file_mappings": self.processed_files,
            "statistics": {
                "total_files": len(self.processed_files),
                "collections": len(self.collections)
            }
        }
        
        reference_file = self.output_folder / "file_reference.json"
        with open(reference_file, 'w', encoding='utf-8') as f:
            json.dump(reference_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Created reference file: {reference_file}")
    
    def run(self):
        """Run the book translation extraction process"""
        print("=" * 60)
        print("Book Translation Extractor")
        print("=" * 60)
        
        # Create output folder
        if self.output_folder.exists():
            print(f"🗑️  Removing existing folder: {self.output_folder}")
            shutil.rmtree(self.output_folder)
        
        self.output_folder.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created output folder: {self.output_folder}")
        
        # Process all collections
        for collection in self.collections:
            self.scan_collection(collection)
        
        # Create reference file
        self.create_reference_file()
        
        print(f"\n✅ Extraction complete!")
        print(f"📊 Statistics:")
        print(f"   - Collections processed: {len(self.collections)}")
        print(f"   - Book files processed: {len(self.processed_files)}")
        print(f"   - Output folder: {self.output_folder}")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Translate the JSON files in '{self.output_folder}' folder")
        print(f"   2. Use Google Gemini or your preferred translation tool")
        print(f"   3. Run apply_book_translations.py to copy back to original files")


def main():
    extractor = BookTranslationExtractor()
    extractor.run()


if __name__ == "__main__":
    main()