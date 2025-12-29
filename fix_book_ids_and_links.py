#!/usr/bin/env python3
"""
Fix Book IDs and Links Script
Verifies and fixes all IDs and chapter links in book.json files to ensure consistency.
"""

import json
from pathlib import Path
import re

class BookIDAndLinkFixer:
    def __init__(self):
        self.collections = [
            "Dīghanikāyo",
            "Majjhimanikāye", 
            "Saṃyuttanikāyo",
            "Aṅguttaranikāyo"
        ]
        self.fixed_count = 0
        self.error_count = 0
        self.issues_found = []
    
    def normalize_id(self, text):
        """Convert text to a normalized ID format"""
        if not text:
            return ""
        
        # Remove diacritics and convert to lowercase
        normalized = text.lower()
        
        # Common ID mappings for Buddhist texts
        id_mappings = {
            'dīghanikāyo': 'dighanikaya',
            'majjhimanikāye': 'majjhimanikaye', 
            'saṃyuttanikāyo': 'samyuttanikaya',
            'aṅguttaranikāyo': 'anguttaranikaya',
            'suttapiṭaka': 'sutta',
            'vinayapiṭaka': 'vinaya',
            'abhidhammapiṭaka': 'abhidhamma',
            'mahāvaggapāḷi': 'mahavaggapali',
            'pāthikavaggapāḷi': 'pathikavaggapali',
            'sīlakkhandhavaggapāḷi': 'silakkhandhavaggapali',
            'majjhimapaṇṇāsapāḷi': 'majjhimapannasapali',
            'mūlapaṇṇāsapāḷi': 'mulapannasapali',
            'uparipaṇṇāsapāḷi': 'uparipannasapali',
            'khandhavaggo': 'khandhavaggo',
            'nidānavaggo': 'nidanavaggo',
            'sagāthāvaggo': 'sagathavaggo',
            'saḷāyatanavaggo': 'salayatanavaggo',
            'mahāvaggo': 'mahavaggo'
        }
        
        # Apply specific mappings
        for pali, id_form in id_mappings.items():
            if pali in normalized:
                return id_form
        
        # Generic normalization
        normalized = re.sub(r'[āĀ]', 'a', normalized)
        normalized = re.sub(r'[īĪ]', 'i', normalized)
        normalized = re.sub(r'[ūŪ]', 'u', normalized)
        normalized = re.sub(r'[ṃṂ]', 'm', normalized)
        normalized = re.sub(r'[ṇṆ]', 'n', normalized)
        normalized = re.sub(r'[ṭṬ]', 't', normalized)
        normalized = re.sub(r'[ḍḌ]', 'd', normalized)
        normalized = re.sub(r'[ḷḶ]', 'l', normalized)
        normalized = re.sub(r'[ṅṄ]', 'n', normalized)
        normalized = re.sub(r'[ñÑ]', 'n', normalized)
        
        # Remove non-alphanumeric characters
        normalized = re.sub(r'[^a-z0-9]', '', normalized)
        
        return normalized
    
    def get_expected_chapter_link(self, collection_name, book_name, chapter_id, chapter_title_pali):
        """Generate expected chapter link based on collection and book"""
        collection_folder = collection_name
        book_folder = book_name
        # Chapter files use format: {id}-{pali_title}.json
        return f"{collection_folder}/{book_folder}/chapters/{chapter_id}-{chapter_title_pali}.json"
    
    def fix_book_file(self, book_path, collection_name, book_name):
        """Fix IDs and links in a single book.json file"""
        try:
            with open(book_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            updated = False
            issues = []
            
            # Fix basket ID
            if 'basket' in book_data and 'id' in book_data['basket']:
                expected_basket_id = self.normalize_id(book_data['basket'].get('name', {}).get('pali', ''))
                if expected_basket_id and book_data['basket']['id'] != expected_basket_id:
                    issues.append(f"Basket ID: {book_data['basket']['id']} → {expected_basket_id}")
                    book_data['basket']['id'] = expected_basket_id
                    updated = True
            
            # Fix collection ID
            if 'collection' in book_data and 'id' in book_data['collection']:
                expected_collection_id = self.normalize_id(collection_name)
                if book_data['collection']['id'] != expected_collection_id:
                    issues.append(f"Collection ID: {book_data['collection']['id']} → {expected_collection_id}")
                    book_data['collection']['id'] = expected_collection_id
                    updated = True
            
            # Fix book/nipata/vagga/pannasa ID
            book_id_field = None
            if 'nipata' in book_data:
                book_id_field = 'nipata'
            elif 'vagga' in book_data:
                book_id_field = 'vagga'
            elif 'pannasa' in book_data:
                book_id_field = 'pannasa'
            
            if book_id_field and 'id' in book_data[book_id_field]:
                expected_book_id = self.normalize_id(book_name)
                if book_data[book_id_field]['id'] != expected_book_id:
                    issues.append(f"{book_id_field.title()} ID: {book_data[book_id_field]['id']} → {expected_book_id}")
                    book_data[book_id_field]['id'] = expected_book_id
                    updated = True
            
            # Fix main book ID
            if 'id' in book_data:
                expected_main_id = self.normalize_id(book_name)
                if book_data['id'] != expected_main_id:
                    issues.append(f"Main ID: {book_data['id']} → {expected_main_id}")
                    book_data['id'] = expected_main_id
                    updated = True
            
            # Fix chapter links
            if 'chapters' in book_data:
                for i, chapter in enumerate(book_data['chapters']):
                    if 'id' in chapter and 'link' in chapter and 'title' in chapter:
                        chapter_id = chapter['id']
                        chapter_title_pali = chapter['title'].get('pali', '')
                        expected_link = self.get_expected_chapter_link(collection_name, book_name, chapter_id, chapter_title_pali)
                        
                        if chapter['link'] != expected_link:
                            issues.append(f"Chapter {i+1} link: {chapter['link']} → {expected_link}")
                            chapter['link'] = expected_link
                            updated = True
            
            # Save if updated
            if updated:
                with open(book_path, 'w', encoding='utf-8') as f:
                    json.dump(book_data, f, ensure_ascii=False, indent=2)
                
                self.issues_found.extend([f"{collection_name}/{book_name}: {issue}" for issue in issues])
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error fixing {book_path}: {e}")
            self.error_count += 1
            return False
    
    def scan_collection(self, collection_name):
        """Scan and fix all books in a collection"""
        collection_path = Path(collection_name)
        
        if not collection_path.exists():
            print(f"⚠️  Collection not found: {collection_name}")
            return
        
        print(f"📚 Fixing {collection_name}...")
        
        # Get all book folders
        book_folders = [f for f in collection_path.iterdir() 
                       if f.is_dir() and f.name.lower() != "pdfs"]
        
        fixed_count = 0
        
        for book_folder in book_folders:
            book_json_path = book_folder / "book.json"
            if book_json_path.exists():
                if self.fix_book_file(book_json_path, collection_name, book_folder.name):
                    fixed_count += 1
                    print(f"  ✓ Fixed: {book_folder.name}")
                else:
                    print(f"  ✓ OK: {book_folder.name}")
        
        self.fixed_count += fixed_count
        print(f"  📊 {collection_name}: {fixed_count} books fixed")
    
    def run(self):
        """Run the ID and link fixing process"""
        print("=" * 60)
        print("Book ID and Link Fixer")
        print("=" * 60)
        
        # Fix all collections
        for collection in self.collections:
            self.scan_collection(collection)
        
        print(f"\n✅ ID and link fixing complete!")
        print(f"📊 Results:")
        print(f"   - Books fixed: {self.fixed_count}")
        print(f"   - Errors: {self.error_count}")
        print(f"   - Issues found: {len(self.issues_found)}")
        
        if self.issues_found:
            print(f"\n🔧 Issues fixed:")
            for issue in self.issues_found[:10]:  # Show first 10 issues
                print(f"   - {issue}")
            if len(self.issues_found) > 10:
                print(f"   ... and {len(self.issues_found) - 10} more")
        
        if self.fixed_count > 0:
            print(f"\n🎉 Success! All IDs and links have been standardized.")


def main():
    fixer = BookIDAndLinkFixer()
    fixer.run()


if __name__ == "__main__":
    main()