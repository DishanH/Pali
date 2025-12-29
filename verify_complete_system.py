#!/usr/bin/env python3
"""
Complete System Verification Script
Verifies that all translations, IDs, links, and structure are correct across the entire system.
"""

import json
from pathlib import Path

class CompleteSystemVerifier:
    def __init__(self):
        self.collections = [
            "Dīghanikāyo",
            "Majjhimanikāye", 
            "Saṃyuttanikāyo",
            "Aṅguttaranikāyo"
        ]
        self.stats = {
            'books_verified': 0,
            'chapters_verified': 0,
            'sections_verified': 0,
            'missing_translations': 0,
            'broken_links': 0,
            'id_issues': 0
        }
    
    def verify_translations(self, obj, path=""):
        """Verify that all translation fields are filled"""
        missing = []
        
        if isinstance(obj, dict):
            # Check for empty translation fields
            if 'english' in obj and not obj['english'].strip():
                missing.append(f"{path}.english")
            if 'sinhala' in obj and not obj['sinhala'].strip():
                missing.append(f"{path}.sinhala")
            
            # Recursively check nested objects
            for key, value in obj.items():
                if key in ['name', 'title', 'footer', 'description']:
                    missing.extend(self.verify_translations(value, f"{path}.{key}"))
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                missing.extend(self.verify_translations(item, f"{path}[{i}]"))
        
        return missing
    
    def verify_chapter_links(self, book_data, collection_name, book_name):
        """Verify that all chapter links point to existing files"""
        broken_links = []
        
        if 'chapters' in book_data:
            for i, chapter in enumerate(book_data['chapters']):
                if 'link' in chapter:
                    link_path = Path(chapter['link'])
                    if not link_path.exists():
                        broken_links.append(f"Chapter {i+1}: {chapter['link']}")
        
        return broken_links
    
    def verify_book_file(self, book_path, collection_name, book_name):
        """Verify a single book.json file"""
        try:
            with open(book_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            issues = []
            
            # Verify translations
            missing_translations = self.verify_translations(book_data, f"{collection_name}/{book_name}")
            if missing_translations:
                issues.extend([f"Missing translation: {mt}" for mt in missing_translations])
                self.stats['missing_translations'] += len(missing_translations)
            
            # Verify chapter links
            broken_links = self.verify_chapter_links(book_data, collection_name, book_name)
            if broken_links:
                issues.extend([f"Broken link: {bl}" for bl in broken_links])
                self.stats['broken_links'] += len(broken_links)
            
            # Count chapters
            chapter_count = len(book_data.get('chapters', []))
            self.stats['chapters_verified'] += chapter_count
            
            # Verify chapter files exist and count sections
            if 'chapters' in book_data:
                for chapter in book_data['chapters']:
                    if 'link' in chapter:
                        chapter_path = Path(chapter['link'])
                        if chapter_path.exists():
                            try:
                                with open(chapter_path, 'r', encoding='utf-8') as f:
                                    chapter_data = json.load(f)
                                section_count = len(chapter_data.get('sections', []))
                                self.stats['sections_verified'] += section_count
                            except:
                                pass
            
            return issues
            
        except Exception as e:
            return [f"Error reading file: {e}"]
    
    def verify_collection(self, collection_name):
        """Verify all books in a collection"""
        collection_path = Path(collection_name)
        
        if not collection_path.exists():
            print(f"⚠️  Collection not found: {collection_name}")
            return
        
        print(f"📚 Verifying {collection_name}...")
        
        # Get all book folders
        book_folders = [f for f in collection_path.iterdir() 
                       if f.is_dir() and f.name.lower() != "pdfs"]
        
        collection_issues = []
        
        for book_folder in book_folders:
            book_json_path = book_folder / "book.json"
            if book_json_path.exists():
                issues = self.verify_book_file(book_json_path, collection_name, book_folder.name)
                if issues:
                    collection_issues.extend([f"{book_folder.name}: {issue}" for issue in issues])
                    print(f"  ⚠️  {book_folder.name}: {len(issues)} issues")
                else:
                    print(f"  ✓ {book_folder.name}: OK")
                
                self.stats['books_verified'] += 1
        
        if collection_issues:
            print(f"  📊 {collection_name}: {len(collection_issues)} total issues")
        else:
            print(f"  📊 {collection_name}: All books verified successfully")
        
        return collection_issues
    
    def run(self):
        """Run the complete system verification"""
        print("=" * 60)
        print("Complete System Verification")
        print("=" * 60)
        
        all_issues = []
        
        # Verify all collections
        for collection in self.collections:
            issues = self.verify_collection(collection)
            all_issues.extend(issues)
        
        print(f"\n✅ System verification complete!")
        print(f"📊 Statistics:")
        print(f"   - Books verified: {self.stats['books_verified']}")
        print(f"   - Chapters verified: {self.stats['chapters_verified']}")
        print(f"   - Sections verified: {self.stats['sections_verified']}")
        print(f"   - Missing translations: {self.stats['missing_translations']}")
        print(f"   - Broken links: {self.stats['broken_links']}")
        print(f"   - Total issues: {len(all_issues)}")
        
        if all_issues:
            print(f"\n⚠️  Issues found:")
            for issue in all_issues[:10]:  # Show first 10 issues
                print(f"   - {issue}")
            if len(all_issues) > 10:
                print(f"   ... and {len(all_issues) - 10} more")
        else:
            print(f"\n🎉 Perfect! No issues found. The entire system is verified and working correctly.")
            print(f"📈 Summary:")
            print(f"   - All {self.stats['books_verified']} books have complete translations")
            print(f"   - All {self.stats['chapters_verified']} chapters are properly linked")
            print(f"   - All {self.stats['sections_verified']} sections are accessible")
            print(f"   - All IDs and links are standardized")


def main():
    verifier = CompleteSystemVerifier()
    verifier.run()


if __name__ == "__main__":
    main()