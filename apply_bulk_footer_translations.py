#!/usr/bin/env python3
"""
Apply Bulk Footer Translations Script
Reads the completed bulk_footer_translations.json file and applies all footer translations
back to the source JSON files.
"""

import json
from pathlib import Path

class BulkFooterTranslationApplier:
    def __init__(self):
        self.translations = {}  # pali -> {english, sinhala}
        self.applied_count = 0
        self.error_count = 0
        
        # Collections to update
        self.collections = [
            "Dīghanikāyo",
            "Majjhimanikāye", 
            "Saṃyuttanikāyo",
            "Aṅguttaranikāyo"
        ]
    
    def load_bulk_footer_translations(self, json_file="bulk_footer_translations.json"):
        """Load footer translations from the bulk translation file"""
        json_path = Path(json_file)
        
        if not json_path.exists():
            print(f"❌ Bulk footer translation file not found: {json_file}")
            print("Please run extract_missing_footers.py first and complete the translations")
            return False
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            translations_data = data.get('translations', {})
            loaded_count = 0
            
            for pali_text, info in translations_data.items():
                english = info.get('english', '').strip()
                sinhala = info.get('sinhala', '').strip()
                
                if english or sinhala:  # At least one translation provided
                    self.translations[pali_text] = {
                        'english': english,
                        'sinhala': sinhala
                    }
                    loaded_count += 1
            
            print(f"✓ Loaded {loaded_count} footer translations from {json_file}")
            
            if loaded_count == 0:
                print("⚠️  No completed footer translations found in the file")
                print("Please fill in the 'english' and 'sinhala' fields in the JSON file")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading bulk footer translations: {e}")
            return False
    
    def apply_footer_translation(self, obj):
        """Apply footer translation to a footer object"""
        if not isinstance(obj, dict):
            return False
        
        pali_text = obj.get('pali', '').strip()
        if not pali_text or pali_text not in self.translations:
            return False
        
        applied = False
        translation = self.translations[pali_text]
        
        # Apply English translation
        if translation['english']:
            if not obj.get('english') or obj.get('english', '').strip() == '':
                obj['english'] = translation['english']
                applied = True
        
        # Apply Sinhala translation
        if translation['sinhala']:
            if not obj.get('sinhala') or obj.get('sinhala', '').strip() == '':
                obj['sinhala'] = translation['sinhala']
                applied = True
        
        return applied
    
    def update_book_file(self, book_path):
        """Update a book.json file with footer translations"""
        try:
            with open(book_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            updated = False
            
            # Update footer
            footer = book_data.get('footer', {})
            if isinstance(footer, dict) and self.apply_footer_translation(footer):
                updated = True
            
            # Save if updated
            if updated:
                with open(book_path, 'w', encoding='utf-8') as f:
                    json.dump(book_data, f, ensure_ascii=False, indent=2)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error updating {book_path}: {e}")
            self.error_count += 1
            return False
    
    def update_chapter_file(self, chapter_path):
        """Update a chapter JSON file with footer translations"""
        try:
            with open(chapter_path, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            updated = False
            
            # Update footer
            footer = chapter_data.get('footer', {})
            if isinstance(footer, dict) and self.apply_footer_translation(footer):
                updated = True
            
            # Save if updated
            if updated:
                with open(chapter_path, 'w', encoding='utf-8') as f:
                    json.dump(chapter_data, f, ensure_ascii=False, indent=2)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error updating {chapter_path}: {e}")
            self.error_count += 1
            return False
    
    def update_collection(self, collection_name):
        """Update all files in a collection"""
        collection_path = Path(collection_name)
        
        if not collection_path.exists():
            print(f"⚠️  Collection not found: {collection_name}")
            return
        
        print(f"\n📚 Updating {collection_name}...")
        
        # Get all book folders
        book_folders = [f for f in collection_path.iterdir() 
                       if f.is_dir() and f.name.lower() != "pdfs"]
        
        collection_updates = 0
        
        for book_folder in book_folders:
            # Update book.json
            book_json_path = book_folder / "book.json"
            if book_json_path.exists():
                if self.update_book_file(book_json_path):
                    collection_updates += 1
            
            # Update chapter files
            chapters_folder = book_folder / "chapters"
            if chapters_folder.exists():
                chapter_files = list(chapters_folder.glob("*.json"))
                for chapter_file in chapter_files:
                    if self.update_chapter_file(chapter_file):
                        collection_updates += 1
        
        self.applied_count += collection_updates
        print(f"  ✓ {collection_name}: {collection_updates} files updated")
    
    def run(self, bulk_file="bulk_footer_translations.json"):
        """Run the bulk footer translation application process"""
        print("=" * 60)
        print("Bulk Footer Translation Applier")
        print("=" * 60)
        
        # Load bulk footer translations
        if not self.load_bulk_footer_translations(bulk_file):
            return
        
        print(f"\n📝 Ready to apply {len(self.translations)} footer translations")
        
        # Apply translations to all collections
        for collection in self.collections:
            self.update_collection(collection)
        
        print(f"\n✅ Bulk footer translation application complete!")
        print(f"📊 Results:")
        print(f"   - Files updated: {self.applied_count}")
        print(f"   - Errors: {self.error_count}")
        print(f"   - Footer translations available: {len(self.translations)}")
        
        if self.applied_count > 0:
            print(f"\n🎉 Success! All footer translations have been applied to the source files.")
            print(f"   You can now run the database import script to see the results.")


def main():
    import sys
    
    bulk_file = "bulk_footer_translations.json"
    if len(sys.argv) > 1:
        bulk_file = sys.argv[1]
    
    applier = BulkFooterTranslationApplier()
    applier.run(bulk_file)


if __name__ == "__main__":
    main()