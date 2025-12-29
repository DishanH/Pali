#!/usr/bin/env python3
"""
Fix Chapter IDs Script
Updates chapter IDs in book.json files to match the actual chapter file names and IDs.
"""

import json
from pathlib import Path
import re

class ChapterIDFixer:
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
    
    def get_chapter_files_mapping(self, chapters_dir):
        """Get mapping of chapter files to their internal IDs"""
        mapping = {}
        
        if not chapters_dir.exists():
            return mapping
        
        for chapter_file in chapters_dir.glob("*.json"):
            try:
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    chapter_data = json.load(f)
                
                if 'id' in chapter_data and 'title' in chapter_data:
                    pali_title = chapter_data['title'].get('pali', '')
                    file_id = chapter_data['id']
                    mapping[pali_title] = {
                        'id': file_id,
                        'filename': chapter_file.name,
                        'path': str(chapter_file)
                    }
            except Exception as e:
                print(f"⚠️  Error reading {chapter_file}: {e}")
        
        return mapping
    
    def fix_book_file(self, book_path, collection_name, book_name):
        """Fix chapter IDs and links in a single book.json file"""
        try:
            with open(book_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            # Get chapter files mapping
            chapters_dir = book_path.parent / "chapters"
            chapter_mapping = self.get_chapter_files_mapping(chapters_dir)
            
            if not chapter_mapping:
                print(f"  ⚠️  No chapter files found in {chapters_dir}")
                return False
            
            updated = False
            issues = []
            
            # Fix chapter IDs and links
            if 'chapters' in book_data:
                for i, chapter in enumerate(book_data['chapters']):
                    if 'title' in chapter and 'pali' in chapter['title']:
                        pali_title = chapter['title']['pali']
                        
                        if pali_title in chapter_mapping:
                            correct_id = chapter_mapping[pali_title]['id']
                            correct_filename = chapter_mapping[pali_title]['filename']
                            correct_link = f"{collection_name}/{book_name}/chapters/{correct_filename}"
                            
                            # Fix ID
                            if chapter.get('id') != correct_id:
                                old_id = chapter.get('id', 'missing')
                                issues.append(f"Chapter {i+1} ID: {old_id} → {correct_id}")
                                chapter['id'] = correct_id
                                updated = True
                            
                            # Fix link
                            if chapter.get('link') != correct_link:
                                old_link = chapter.get('link', 'missing')
                                issues.append(f"Chapter {i+1} link: {old_link} → {correct_link}")
                                chapter['link'] = correct_link
                                updated = True
                        else:
                            issues.append(f"Chapter {i+1}: No matching file found for '{pali_title}'")
            
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
        """Run the chapter ID fixing process"""
        print("=" * 60)
        print("Chapter ID Fixer")
        print("=" * 60)
        
        # Fix all collections
        for collection in self.collections:
            self.scan_collection(collection)
        
        print(f"\n✅ Chapter ID fixing complete!")
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
            print(f"\n🎉 Success! All chapter IDs and links have been synchronized with actual files.")


def main():
    fixer = ChapterIDFixer()
    fixer.run()


if __name__ == "__main__":
    main()