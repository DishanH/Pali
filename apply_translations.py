#!/usr/bin/env python3
"""
Apply Translations Script
Reads completed translation files and applies them back to the source JSON files.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

class TranslationApplier:
    def __init__(self):
        self.translations = {
            'english': {},
            'sinhala': {}
        }
        self.applied_count = 0
        self.error_count = 0
        
        # Collections to update
        self.collections = [
            "Dīghanikāyo",
            "Majjhimanikāye", 
            "Saṃyuttanikāyo",
            "Aṅguttaranikāyo"
        ]
    
    def load_translations_from_csv(self, csv_file, language):
        """Load translations from CSV file"""
        if not csv_file.exists():
            print(f"⚠️  Translation file not found: {csv_file}")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pali_text = row['Pali Text'].strip()
                translation = row[f'{language.title()} Translation'].strip()
                
                if pali_text and translation and translation != '':
                    self.translations[language][pali_text] = translation
                    count += 1
        
        print(f"✓ Loaded {count} {language} translations from {csv_file.name}")
        return count
    
    def load_translations_from_json(self, json_file, language):
        """Load translations from JSON file"""
        if not json_file.exists():
            print(f"⚠️  Translation file not found: {json_file}")
            return 0
        
        count = 0
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            for pali_text, info in data.get('translations', {}).items():
                translation = info.get('translation', '').strip()
                if translation:
                    self.translations[language][pali_text] = translation
                    count += 1
        
        print(f"✓ Loaded {count} {language} translations from {json_file.name}")
        return count
    
    def apply_translation_to_field(self, obj, pali_key, english_key, sinhala_key):
        """Apply translation to a specific field in an object"""
        if not isinstance(obj, dict):
            return False
        
        pali_text = obj.get(pali_key, '').strip()
        if not pali_text:
            return False
        
        applied = False
        
        # Apply English translation
        if pali_text in self.translations['english']:
            if not obj.get(english_key) or obj.get(english_key, '').strip() == '':
                obj[english_key] = self.translations['english'][pali_text]
                applied = True
        
        # Apply Sinhala translation
        if pali_text in self.translations['sinhala']:
            if not obj.get(sinhala_key) or obj.get(sinhala_key, '').strip() == '':
                obj[sinhala_key] = self.translations['sinhala'][pali_text]
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
                self.applied_count += 1
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
                    if pali_title in self.translations['english']:
                        if not section.get('englishTitle') or section.get('englishTitle', '').strip() == '':
                            section['englishTitle'] = self.translations['english'][pali_title]
                            updated = True
                    
                    if pali_title in self.translations['sinhala']:
                        if not section.get('sinhalaTitle') or section.get('sinhalaTitle', '').strip() == '':
                            section['sinhalaTitle'] = self.translations['sinhala'][pali_title]
                            updated = True
                
                # Update vagga titles
                if section.get('vagga'):
                    vagga_pali = section['vagga'].strip()
                    if vagga_pali in self.translations['english']:
                        if not section.get('vaggaEnglish') or section.get('vaggaEnglish', '').strip() == '':
                            section['vaggaEnglish'] = self.translations['english'][vagga_pali]
                            updated = True
                    
                    if vagga_pali in self.translations['sinhala']:
                        if not section.get('vaggaSinhala') or section.get('vaggaSinhala', '').strip() == '':
                            section['vaggaSinhala'] = self.translations['sinhala'][vagga_pali]
                            updated = True
            
            # Save if updated
            if updated:
                with open(chapter_path, 'w', encoding='utf-8') as f:
                    json.dump(chapter_data, f, ensure_ascii=False, indent=2)
                self.applied_count += 1
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
        
        for book_folder in book_folders:
            # Update book.json
            book_json_path = book_folder / "book.json"
            if book_json_path.exists():
                self.update_book_file(book_json_path)
            
            # Update chapter files
            chapters_folder = book_folder / "chapters"
            if chapters_folder.exists():
                chapter_files = list(chapters_folder.glob("*.json"))
                for chapter_file in chapter_files:
                    self.update_chapter_file(chapter_file)
        
        print(f"  ✓ {collection_name} updated")
    
    def run(self, translation_dir="missing_translations"):
        """Run the translation application process"""
        print("=" * 60)
        print("Translation Applier")
        print("=" * 60)
        
        translation_path = Path(translation_dir)
        if not translation_path.exists():
            print(f"❌ Translation directory not found: {translation_dir}")
            print("Please run extract_missing_translations.py first")
            return
        
        # Load translations from CSV files (preferred)
        english_csv = translation_path / "missing_english_translations.csv"
        sinhala_csv = translation_path / "missing_sinhala_translations.csv"
        
        english_count = self.load_translations_from_csv(english_csv, 'english')
        sinhala_count = self.load_translations_from_csv(sinhala_csv, 'sinhala')
        
        # Also try JSON files as backup
        if english_count == 0:
            english_json = translation_path / "missing_english_translations.json"
            english_count = self.load_translations_from_json(english_json, 'english')
        
        if sinhala_count == 0:
            sinhala_json = translation_path / "missing_sinhala_translations.json"
            sinhala_count = self.load_translations_from_json(sinhala_json, 'sinhala')
        
        total_translations = english_count + sinhala_count
        if total_translations == 0:
            print("❌ No translations found to apply")
            print("Please add translations to the CSV files first")
            return
        
        print(f"\n📝 Ready to apply {total_translations} translations")
        
        # Apply translations to all collections
        for collection in self.collections:
            self.update_collection(collection)
        
        print(f"\n✅ Translation application complete!")
        print(f"📊 Results:")
        print(f"   - Files updated: {self.applied_count}")
        print(f"   - Errors: {self.error_count}")
        print(f"   - Total translations available: {total_translations}")


def main():
    import sys
    
    translation_dir = "missing_translations"
    if len(sys.argv) > 1:
        translation_dir = sys.argv[1]
    
    applier = TranslationApplier()
    applier.run(translation_dir)


if __name__ == "__main__":
    main()