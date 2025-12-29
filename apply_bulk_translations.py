#!/usr/bin/env python3
"""
Apply Bulk Translations Script
Reads the completed bulk_translations.json file and applies all translations
back to the source JSON files.
"""

import json
from pathlib import Path

class BulkTranslationApplier:
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
    
    def load_bulk_translations(self, json_file="bulk_translations.json"):
        """Load translations from the bulk translation file"""
        json_path = Path(json_file)
        
        if not json_path.exists():
            print(f"❌ Bulk translation file not found: {json_file}")
            print("Please run create_bulk_translation_json.py first and complete the translations")
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
            
            print(f"✓ Loaded {loaded_count} translations from {json_file}")
            
            if loaded_count == 0:
                print("⚠️  No completed translations found in the file")
                print("Please fill in the 'english' and 'sinhala' fields in the JSON file")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading bulk translations: {e}")
            return False
    
    def apply_translation_to_field(self, obj, pali_key, english_key, sinhala_key):
        """Apply translation to a specific field in an object"""
        if not isinstance(obj, dict):
            return False
        
        pali_text = obj.get(pali_key, '').strip()
        if not pali_text or pali_text not in self.translations:
            return False
        
        applied = False
        translation = self.translations[pali_text]
        
        # Apply English translation
        if translation['english']:
            if not obj.get(english_key) or obj.get(english_key, '').strip() == '':
                obj[english_key] = translation['english']
                applied = True
        
        # Apply Sinhala translation
        if translation['sinhala']:
            if not obj.get(sinhala_key) or obj.get(sinhala_key, '').strip() == '':
                obj[sinhala_key] = translation['sinhala']
                applied = True
        
        return applied
    
    def update_book_file(self, book_path):
        """Update a book.json file with translations"""
        try:
            with open(book_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            updated = False
            
            # Update book title
            if self.apply_translation_to_field(
                book_data.get('title', {}), 'pali', 'english', 'sinhala'
            ):
                updated = True
            
            # Update vagga/nipata/pannasa names
            for subdivision_type in ['vagga', 'nipata', 'pannasa']:
                if subdivision_type in book_data:
                    subdivision = book_data[subdivision_type]
                    if self.apply_translation_to_field(
                        subdivision.get('name', {}), 'pali', 'english', 'sinhala'
                    ):
                        updated = True
            
            # Update footer
            if self.apply_translation_to_field(
                book_data.get('footer', {}), 'pali', 'english', 'sinhala'
            ):
                updated = True
            
            # Update chapter metadata
            chapters = book_data.get('chapters', [])
            for chapter in chapters:
                if self.apply_translation_to_field(
                    chapter.get('title', {}), 'pali', 'english', 'sinhala'
                ):
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
        """Update a chapter JSON file with translations"""
        try:
            with open(chapter_path, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            updated = False
            
            # Update chapter title
            if self.apply_translation_to_field(
                chapter_data.get('title', {}), 'pali', 'english', 'sinhala'
            ):
                updated = True
            
            # Update sections
            sections = chapter_data.get('sections', [])
            for section in sections:
                # Update section titles
                if section.get('paliTitle'):
                    pali_title = section['paliTitle'].strip()
                    if pali_title in self.translations:
                        translation = self.translations[pali_title]
                        
                        if translation['english']:
                            if not section.get('englishTitle') or section.get('englishTitle', '').strip() == '':
                                section['englishTitle'] = translation['english']
                                updated = True
                        
                        if translation['sinhala']:
                            if not section.get('sinhalaTitle') or section.get('sinhalaTitle', '').strip() == '':
                                section['sinhalaTitle'] = translation['sinhala']
                                updated = True
                
                # Update vagga titles
                if section.get('vagga'):
                    vagga_pali = section['vagga'].strip()
                    if vagga_pali in self.translations:
                        translation = self.translations[vagga_pali]
                        
                        if translation['english']:
                            if not section.get('vaggaEnglish') or section.get('vaggaEnglish', '').strip() == '':
                                section['vaggaEnglish'] = translation['english']
                                updated = True
                        
                        if translation['sinhala']:
                            if not section.get('vaggaSinhala') or section.get('vaggaSinhala', '').strip() == '':
                                section['vaggaSinhala'] = translation['sinhala']
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
    
    def run(self, bulk_file="bulk_translations.json"):
        """Run the bulk translation application process"""
        print("=" * 60)
        print("Bulk Translation Applier")
        print("=" * 60)
        
        # Load bulk translations
        if not self.load_bulk_translations(bulk_file):
            return
        
        print(f"\n📝 Ready to apply {len(self.translations)} translations")
        
        # Apply translations to all collections
        for collection in self.collections:
            self.update_collection(collection)
        
        print(f"\n✅ Bulk translation application complete!")
        print(f"📊 Results:")
        print(f"   - Files updated: {self.applied_count}")
        print(f"   - Errors: {self.error_count}")
        print(f"   - Translations available: {len(self.translations)}")
        
        if self.applied_count > 0:
            print(f"\n🎉 Success! All translations have been applied to the source files.")
            print(f"   You can now run the database import script to see the results.")


def main():
    import sys
    
    bulk_file = "bulk_translations.json"
    if len(sys.argv) > 1:
        bulk_file = sys.argv[1]
    
    applier = BulkTranslationApplier()
    applier.run(bulk_file)


if __name__ == "__main__":
    main()