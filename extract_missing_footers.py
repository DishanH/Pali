#!/usr/bin/env python3
"""
Missing Footer Extractor
Extracts all missing footer translations from Buddhist text collections
and creates a bulk translation JSON file.
"""

import json
from pathlib import Path
from collections import defaultdict

class MissingFooterExtractor:
    def __init__(self):
        self.missing_footers = {}  # pali -> contexts
        self.stats = {
            'books_scanned': 0,
            'chapters_scanned': 0,
            'footers_found': 0,
            'missing_english': 0,
            'missing_sinhala': 0
        }
        
        # Collections to scan
        self.collections = [
            "Dīghanikāyo",
            "Majjhimanikāye", 
            "Saṃyuttanikāyo",
            "Aṅguttaranikāyo"
        ]
    
    def is_missing_translation(self, text):
        """Check if a translation is missing or empty"""
        return not text or text.strip() == ''
    
    def extract_from_book(self, book_path):
        """Extract missing footer translations from a book.json file"""
        try:
            with open(book_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            # Check footer in book metadata
            footer = book_data.get('footer', {})
            if isinstance(footer, dict):
                pali_footer = footer.get('pali', '').strip()
                english_footer = footer.get('english', '').strip()
                sinhala_footer = footer.get('sinhala', '').strip()
                
                if pali_footer:
                    self.stats['footers_found'] += 1
                    
                    # Check if translations are missing
                    missing_english = self.is_missing_translation(english_footer)
                    missing_sinhala = self.is_missing_translation(sinhala_footer)
                    
                    if missing_english or missing_sinhala:
                        context = f"Book Footer: {book_path.parent.name}/{book_path.name}"
                        
                        if pali_footer not in self.missing_footers:
                            self.missing_footers[pali_footer] = {
                                'contexts': [],
                                'missing_english': missing_english,
                                'missing_sinhala': missing_sinhala
                            }
                        
                        self.missing_footers[pali_footer]['contexts'].append(context)
                        
                        if missing_english:
                            self.stats['missing_english'] += 1
                        if missing_sinhala:
                            self.stats['missing_sinhala'] += 1
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing {book_path}: {e}")
            return False
    
    def extract_from_chapter(self, chapter_path):
        """Extract missing footer translations from a chapter JSON file"""
        try:
            with open(chapter_path, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            # Check footer in chapter metadata
            footer = chapter_data.get('footer', {})
            if isinstance(footer, dict):
                pali_footer = footer.get('pali', '').strip()
                english_footer = footer.get('english', '').strip()
                sinhala_footer = footer.get('sinhala', '').strip()
                
                if pali_footer:
                    self.stats['footers_found'] += 1
                    
                    # Check if translations are missing
                    missing_english = self.is_missing_translation(english_footer)
                    missing_sinhala = self.is_missing_translation(sinhala_footer)
                    
                    if missing_english or missing_sinhala:
                        context = f"Chapter Footer: {chapter_path.parent.parent.name}/{chapter_path.name}"
                        
                        if pali_footer not in self.missing_footers:
                            self.missing_footers[pali_footer] = {
                                'contexts': [],
                                'missing_english': missing_english,
                                'missing_sinhala': missing_sinhala
                            }
                        
                        self.missing_footers[pali_footer]['contexts'].append(context)
                        
                        if missing_english:
                            self.stats['missing_english'] += 1
                        if missing_sinhala:
                            self.stats['missing_sinhala'] += 1
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing {chapter_path}: {e}")
            return False
    
    def scan_collection(self, collection_name):
        """Scan all books and chapters in a collection"""
        collection_path = Path(collection_name)
        
        if not collection_path.exists():
            print(f"⚠️  Collection not found: {collection_name}")
            return
        
        print(f"📚 Scanning {collection_name}...")
        
        # Get all book folders
        book_folders = [f for f in collection_path.iterdir() 
                       if f.is_dir() and f.name.lower() != "pdfs"]
        
        for book_folder in book_folders:
            print(f"  ✓ {book_folder.name}")
            
            # Process book.json
            book_json_path = book_folder / "book.json"
            if book_json_path.exists():
                self.extract_from_book(book_json_path)
                self.stats['books_scanned'] += 1
            
            # Process chapter files
            chapters_folder = book_folder / "chapters"
            if chapters_folder.exists():
                chapter_files = list(chapters_folder.glob("*.json"))
                for chapter_file in chapter_files:
                    self.extract_from_chapter(chapter_file)
                    self.stats['chapters_scanned'] += 1
    
    def generate_bulk_footer_json(self, output_file="bulk_footer_translations.json"):
        """Generate bulk translation JSON file for footers"""
        
        # Create translations dictionary
        translations = {}
        for pali_footer, info in self.missing_footers.items():
            translations[pali_footer] = {
                "pali": pali_footer,
                "english": "",
                "sinhala": "",
                "contexts": info['contexts'],
                "usage_count": len(info['contexts']),
                "originally_needed": {
                    "english": info['missing_english'],
                    "sinhala": info['missing_sinhala']
                }
            }
        
        # Create the complete JSON structure
        bulk_data = {
            "metadata": {
                "created_date": "2025-12-29",
                "total_terms": len(translations),
                "instructions": {
                    "purpose": "Bulk translation of Pali Buddhist footer texts",
                    "task": "Fill in the \"english\" and \"sinhala\" fields for each footer",
                    "context": "Use the \"contexts\" field to understand where each footer is used",
                    "note": "Both English and Sinhala translations are requested for simplicity"
                },
                "statistics": {
                    "books_scanned": self.stats['books_scanned'],
                    "chapters_scanned": self.stats['chapters_scanned'],
                    "footers_found": self.stats['footers_found'],
                    "unique_terms": len(translations)
                }
            },
            "translations": translations
        }
        
        # Write to file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(bulk_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Generated: {output_file}")
        return output_path
    
    def run(self):
        """Run the missing footer extraction process"""
        print("=" * 60)
        print("Missing Footer Extractor")
        print("=" * 60)
        
        # Scan all collections
        for collection in self.collections:
            self.scan_collection(collection)
        
        print(f"\n📊 Generating footer translation files...")
        
        if self.missing_footers:
            # Generate bulk translation file
            self.generate_bulk_footer_json()
            
            print(f"\n✅ Extraction complete!")
            print(f"📈 Statistics:")
            print(f"   - Books scanned: {self.stats['books_scanned']}")
            print(f"   - Chapters scanned: {self.stats['chapters_scanned']}")
            print(f"   - Footers found: {self.stats['footers_found']}")
            print(f"   - Missing English: {self.stats['missing_english']}")
            print(f"   - Missing Sinhala: {self.stats['missing_sinhala']}")
            print(f"   - Unique footer terms: {len(self.missing_footers)}")
            
            print(f"\n💡 Next steps:")
            print(f"   1. Translate the terms in bulk_footer_translations.json")
            print(f"   2. Run apply_bulk_footer_translations.py to apply them")
        else:
            print(f"\n🎉 No missing footer translations found!")
            print(f"📈 Statistics:")
            print(f"   - Books scanned: {self.stats['books_scanned']}")
            print(f"   - Chapters scanned: {self.stats['chapters_scanned']}")
            print(f"   - Footers found: {self.stats['footers_found']}")


def main():
    extractor = MissingFooterExtractor()
    extractor.run()


if __name__ == "__main__":
    main()